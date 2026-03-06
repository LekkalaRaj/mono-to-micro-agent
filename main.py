"""
main.py
────────
CLI entry point for the Monolithic To Microservices pipeline.

Usage
─────
    python main.py https://github.com/your-org/legacy-banking-monolith

    # Optional: override user ID
    python main.py https://github.com/your-org/legacy-banking-monolith --user-id ops-team-001
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from runner.pipeline_runner import PipelineRunner


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Monolithic To Microservices - Multi-Agent Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "github_url",
        nargs="?",
        default="https://github.com/your-org/legacy-banking-monolith",
        help="GitHub repository URL of the Java monolith to migrate",
    )
    parser.add_argument(
        "--user-id",
        default=None,
        help="Session user ID override (default: value from settings)",
    )
    return parser.parse_args()


async def _main() -> int:
    args   = parse_args()
    runner = PipelineRunner(user_id=args.user_id)
    result = await runner.run(args.github_url)
    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(_main()))