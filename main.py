import argparse
import logging
import sys
import os
from dotenv import load_dotenv
from src.core.engine import WorkflowEngine

# Load environment variables from .env file
load_dotenv()


def setup_logging(debug: bool = False):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main():
    parser = argparse.ArgumentParser(
        description="Cognitive Engine: Workflow Automation Platform"
    )
    parser.add_argument(
        "--workflow",
        type=str,
        required=True,
        help="Path to the YAML workflow configuration file.",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging.")

    args = parser.parse_args()
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)

    if not os.path.exists(args.workflow):
        logger.error(f"Workflow file not found: {args.workflow}")
        sys.exit(1)

    try:
        engine = WorkflowEngine(args.workflow)
        engine.run()
    except Exception as e:
        logger.critical(f"Fatal error during execution: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
