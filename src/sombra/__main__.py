"""Entry point for running as a module: python -m sombra"""

import logging
import sys


def main() -> int:
    """Main entry point."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )

    from .app import main as app_main

    return app_main()


if __name__ == "__main__":
    sys.exit(main())
