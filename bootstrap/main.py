#!/usr/bin/env python3
"""
CoratiaOS Bootstrap — Entry point.
Manages the lifecycle of the CoratiaOS core container.
"""
import asyncio
import logging
import sys

from bootstrap.bootstrap import Bootstrapper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("coratiaos-bootstrap")


def main() -> None:
    logger.info("Starting CoratiaOS Bootstrap...")
    bootstrapper = Bootstrapper()
    try:
        asyncio.run(bootstrapper.run())
    except KeyboardInterrupt:
        logger.info("Bootstrap interrupted by user.")
    except Exception as e:
        logger.critical(f"Bootstrap failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
