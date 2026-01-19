"""Entry point for PyInstaller builds."""

import logging
import sys
import os

# Add src to path for frozen builds
if getattr(sys, 'frozen', False):
    # Running as compiled
    base_path = sys._MEIPASS
else:
    # Running as script
    base_path = os.path.dirname(os.path.abspath(__file__))


def main() -> int:
    """Main entry point."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )

    from sombra.app import main as app_main

    return app_main()


if __name__ == "__main__":
    sys.exit(main())
