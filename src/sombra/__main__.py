"""Entry point for running as a module: python -m sombra"""

import sys


def main() -> int:
    """Main entry point."""
    # Configure logging first
    from .core.logging_config import setup_logging
    setup_logging()

    from .app import main as app_main

    return app_main()


if __name__ == "__main__":
    sys.exit(main())
