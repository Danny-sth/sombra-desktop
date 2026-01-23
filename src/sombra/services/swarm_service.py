"""Swarm API service for agent orchestration.

Connects to SwarmServer running on PC (port 8081) for:
- Task management (start, approve, reject, stop)
- Status monitoring via SSE
- Agent output streaming
- Question handling
"""

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

import httpx
from httpx_sse import aconnect_sse
from PySide6.QtCore import QObject, Signal

from ..config.settings import get_settings
from ..core.async_bridge import get_async_bridge

logger = logging.getLogger(__name__)


class SwarmMode(Enum):
    """Swarm operational mode."""
    DEVELOPMENT = "development"
    QA = "qa"


class AgentRole(Enum):
    """Agent roles in the swarm."""
    BUILDER = "builder"
    REVIEWER = "reviewer"
    TESTER = "tester"
    REFACTOR = "refactor"


class AgentStatus(Enum):
    """Agent status."""
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    ERROR = "error"
    STOPPED = "stopped"


class TaskStatus(Enum):
    """Swarm task status."""
    PENDING = "pending"
    DECOMPOSING = "decomposing"
    RUNNING = "running"
    REVIEWING = "reviewing"
    TESTING = "testing"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"
    RUNNING_PYTEST = "running_pytest"
    PUSHING_CI = "pushing_ci"
    WAITING_CI = "waiting_ci"
    RUNNING_QA = "running_qa"
    ANALYZING_FAILURES = "analyzing_failures"
    GENERATING_REPORT = "generating_report"
    WAITING_FOR_INPUT = "waiting_for_input"


@dataclass
class SwarmAgent:
    """Agent state data."""
    role: AgentRole
    status: AgentStatus = AgentStatus.IDLE
    worktree_path: str = ""
    current_subtask: Optional[dict] = None
    last_output: Optional[str] = None
    iterations: int = 0
    usage: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, role_str: str, data: dict) -> "SwarmAgent":
        """Create from API dict."""
        return cls(
            role=AgentRole(role_str),
            status=AgentStatus(data.get("status", "idle")),
            worktree_path=data.get("worktree_path", ""),
            current_subtask=data.get("current_subtask"),
            last_output=data.get("last_output"),
            iterations=data.get("iterations", 0),
            usage=data.get("usage", {}),
        )


@dataclass
class SwarmTask:
    """Current task data."""
    id: str
    description: str
    target_project: str
    status: TaskStatus
    mode: SwarmMode
    subtasks: list[dict] = field(default_factory=list)
    branch_name: str = ""
    changed_files: list[str] = field(default_factory=list)
    pytest_passed: bool = False
    ci_status: Optional[str] = None
    ci_url: Optional[str] = None
    pr_url: Optional[str] = None
    pending_question: Optional[str] = None
    question_options: list[str] = field(default_factory=list)
    final_report: Optional[str] = None
    error: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "SwarmTask":
        """Create from API dict."""
        return cls(
            id=data.get("id", ""),
            description=data.get("description", ""),
            target_project=data.get("target_project", ""),
            status=TaskStatus(data.get("status", "pending")),
            mode=SwarmMode(data.get("mode", "development")),
            subtasks=data.get("subtasks", []),
            branch_name=data.get("branch_name", ""),
            changed_files=data.get("changed_files", []),
            pytest_passed=data.get("pytest_passed", False),
            ci_status=data.get("ci_status"),
            ci_url=data.get("ci_url"),
            pr_url=data.get("pr_url"),
            pending_question=data.get("pending_question"),
            question_options=data.get("question_options", []),
            final_report=data.get("final_report"),
            error=data.get("error"),
        )


@dataclass
class SwarmState:
    """Full swarm state."""
    is_running: bool = False
    current_task: Optional[SwarmTask] = None
    agents: dict[AgentRole, SwarmAgent] = field(default_factory=dict)
    total_cost_usd: float = 0.0
    total_iterations: int = 0
    total_duration_seconds: Optional[float] = None

    @classmethod
    def from_dict(cls, data: dict) -> "SwarmState":
        """Create from API dict."""
        agents = {}
        for role_str, agent_data in data.get("agents", {}).items():
            try:
                agents[AgentRole(role_str)] = SwarmAgent.from_dict(role_str, agent_data)
            except ValueError:
                pass  # Unknown role

        current_task = None
        if data.get("current_task"):
            current_task = SwarmTask.from_dict(data["current_task"])

        return cls(
            is_running=data.get("is_running", False),
            current_task=current_task,
            agents=agents,
            total_cost_usd=data.get("total_cost_usd", 0.0),
            total_iterations=data.get("total_iterations", 0),
            total_duration_seconds=data.get("total_duration_seconds"),
        )


class SwarmService(QObject):
    """Swarm API client with SSE streaming support.

    Connects to SwarmServer (default: http://localhost:8081) for
    orchestrating Claude Code agent swarm.
    """

    # Signals
    state_updated = Signal(object)  # SwarmState
    agent_output = Signal(str, str)  # agent_role, message
    task_started = Signal(str)  # task_id
    task_completed = Signal(str, bool)  # task_id, success
    question_received = Signal(str, list)  # question, options
    connection_status = Signal(str)  # status message
    error_occurred = Signal(str)  # error message

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)

        settings = get_settings()
        # Swarm server runs on PC, default port 8081
        self._base_url = settings.swarm_api_url
        self._client: Optional[httpx.AsyncClient] = None
        self._cancel_requested = False
        self._state = SwarmState()

    @property
    def state(self) -> SwarmState:
        """Get current swarm state."""
        return self._state

    @property
    def is_running(self) -> bool:
        """Check if swarm is running."""
        return self._state.is_running

    async def _ensure_client(self) -> httpx.AsyncClient:
        """Ensure HTTP client is initialized."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=60.0)
        return self._client

    # ===== Task Management =====

    async def start_task(
        self,
        description: str,
        mode: SwarmMode = SwarmMode.DEVELOPMENT,
        project: Optional[str] = None,
    ) -> Optional[SwarmTask]:
        """Start a new swarm task.

        Args:
            description: Task description.
            mode: Operational mode (DEVELOPMENT or QA).
            project: Target project path (optional).

        Returns:
            SwarmTask if started successfully, None otherwise.
        """
        client = await self._ensure_client()

        payload: dict[str, Any] = {
            "description": description,
            "mode": mode.value,
        }
        if project:
            payload["project"] = project

        try:
            response = await client.post(
                f"{self._base_url}/api/swarm/task/start",
                json=payload,
            )
            response.raise_for_status()

            data = response.json()
            task = SwarmTask.from_dict(data)
            self.task_started.emit(task.id)
            logger.info(f"Swarm task started: {task.id}")
            return task

        except httpx.HTTPError as e:
            error_msg = f"Failed to start task: {e}"
            self.error_occurred.emit(error_msg)
            logger.error(error_msg)
            return None

    async def approve_task(self) -> bool:
        """Approve current task."""
        client = await self._ensure_client()

        try:
            response = await client.post(f"{self._base_url}/api/swarm/task/approve")
            response.raise_for_status()
            data = response.json()
            return data.get("success", False)
        except httpx.HTTPError as e:
            self.error_occurred.emit(f"Failed to approve task: {e}")
            return False

    async def reject_task(self, reason: str = "") -> bool:
        """Reject current task."""
        client = await self._ensure_client()

        try:
            response = await client.post(
                f"{self._base_url}/api/swarm/task/reject",
                json={"reason": reason},
            )
            response.raise_for_status()
            data = response.json()
            return data.get("success", False)
        except httpx.HTTPError as e:
            self.error_occurred.emit(f"Failed to reject task: {e}")
            return False

    async def stop_task(self) -> bool:
        """Stop current task."""
        client = await self._ensure_client()

        try:
            response = await client.post(f"{self._base_url}/api/swarm/task/stop")
            response.raise_for_status()
            data = response.json()
            return data.get("success", False)
        except httpx.HTTPError as e:
            self.error_occurred.emit(f"Failed to stop task: {e}")
            return False

    async def answer_question(self, answer: str) -> bool:
        """Answer pending question."""
        client = await self._ensure_client()

        try:
            response = await client.post(
                f"{self._base_url}/api/swarm/answer",
                json={"answer": answer},
            )
            response.raise_for_status()
            data = response.json()
            return data.get("success", False)
        except httpx.HTTPError as e:
            self.error_occurred.emit(f"Failed to answer question: {e}")
            return False

    # ===== Status =====

    async def get_status(self) -> SwarmState:
        """Get current swarm status."""
        client = await self._ensure_client()

        try:
            response = await client.get(f"{self._base_url}/api/swarm/status")
            response.raise_for_status()
            data = response.json()
            self._state = SwarmState.from_dict(data)
            return self._state
        except httpx.HTTPError as e:
            logger.warning(f"Failed to get swarm status: {e}")
            return self._state

    async def check_connection(self) -> bool:
        """Check if swarm server is reachable."""
        try:
            client = await self._ensure_client()
            response = await client.get(
                f"{self._base_url}/api/swarm/health",
                timeout=5.0,
            )
            return response.status_code == 200
        except Exception:
            return False

    # ===== SSE Streaming =====

    async def listen_status_stream(self) -> None:
        """Listen to SSE status stream and emit updates."""
        client = await self._ensure_client()
        self._cancel_requested = False

        try:
            async with aconnect_sse(
                client,
                "GET",
                f"{self._base_url}/api/swarm/status/sse",
            ) as sse:
                self.connection_status.emit("Connected to Swarm")

                async for event in sse.aiter_sse():
                    if self._cancel_requested:
                        break

                    if event.data:
                        try:
                            data = json.loads(event.data)
                            self._state = SwarmState.from_dict(data)
                            self.state_updated.emit(self._state)

                            # Check for pending question
                            if (self._state.current_task and
                                self._state.current_task.pending_question):
                                self.question_received.emit(
                                    self._state.current_task.pending_question,
                                    self._state.current_task.question_options,
                                )

                        except json.JSONDecodeError:
                            pass

        except httpx.HTTPError as e:
            self.connection_status.emit(f"Disconnected: {e}")
            logger.warning(f"Status stream error: {e}")

    async def listen_output_stream(self) -> None:
        """Listen to SSE agent output stream."""
        client = await self._ensure_client()
        self._cancel_requested = False

        try:
            async with aconnect_sse(
                client,
                "GET",
                f"{self._base_url}/api/swarm/output/sse",
            ) as sse:
                async for event in sse.aiter_sse():
                    if self._cancel_requested:
                        break

                    if event.data:
                        try:
                            data = json.loads(event.data)
                            agent = data.get("agent", "unknown")
                            message = data.get("message", "")
                            self.agent_output.emit(agent, message)
                        except json.JSONDecodeError:
                            pass

        except httpx.HTTPError as e:
            logger.warning(f"Output stream error: {e}")

    # ===== Async Wrappers =====

    def start_task_async(
        self,
        description: str,
        mode: SwarmMode = SwarmMode.DEVELOPMENT,
        project: Optional[str] = None,
    ) -> None:
        """Non-blocking task start."""
        bridge = get_async_bridge()
        bridge.run_coroutine(self.start_task(description, mode, project))

    def approve_task_async(self) -> None:
        """Non-blocking approve."""
        bridge = get_async_bridge()
        bridge.run_coroutine(self.approve_task())

    def reject_task_async(self, reason: str = "") -> None:
        """Non-blocking reject."""
        bridge = get_async_bridge()
        bridge.run_coroutine(self.reject_task(reason))

    def stop_task_async(self) -> None:
        """Non-blocking stop."""
        bridge = get_async_bridge()
        bridge.run_coroutine(self.stop_task())

    def answer_question_async(self, answer: str) -> None:
        """Non-blocking answer."""
        bridge = get_async_bridge()
        bridge.run_coroutine(self.answer_question(answer))

    def get_status_async(self) -> None:
        """Non-blocking status fetch."""
        bridge = get_async_bridge()
        bridge.run_coroutine(self.get_status())

    def check_connection_async(self) -> None:
        """Non-blocking connection check."""
        async def do_check() -> None:
            connected = await self.check_connection()
            if connected:
                self.connection_status.emit("Connected to Swarm")
            else:
                self.connection_status.emit("Swarm server not available")

        bridge = get_async_bridge()
        bridge.run_coroutine(do_check())

    def start_status_stream(self) -> None:
        """Start listening to status stream in background."""
        bridge = get_async_bridge()
        bridge.run_coroutine(self.listen_status_stream())

    def start_output_stream(self) -> None:
        """Start listening to output stream in background."""
        bridge = get_async_bridge()
        bridge.run_coroutine(self.listen_output_stream())

    def stop_streams(self) -> None:
        """Stop all SSE streams."""
        self._cancel_requested = True

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def cleanup(self) -> None:
        """Clean up resources."""
        self.stop_streams()
        bridge = get_async_bridge()
        if bridge.is_running:
            bridge.run_coroutine(self.close())


# Singleton instance
_swarm_service: Optional[SwarmService] = None


def get_swarm_service() -> SwarmService:
    """Get or create SwarmService singleton."""
    global _swarm_service
    if _swarm_service is None:
        _swarm_service = SwarmService()
    return _swarm_service
