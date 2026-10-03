"""Command-line interface entry point for GitHub Activity CLI."""

import argparse
import sys

from github_client import (
    GitHubAPIError,
    NetworkError,
    RateLimitExceededError,
    UserNotFoundError,
    fetch_user_events,
)
from formatter import format_activities


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="github-activity",
        description="Fetch and display the recent public activity of a specified GitHub user.",
    )
    parser.add_argument(
        "username",
        type=str,
        help="GitHub username to fetch activity for.",
    )
    parser.add_argument(
        "-n",
        "--limit",
        type=int,
        default=10,
        help="Maximum number of events to display (default: 10).",
    )
    parser.add_argument(
        "-t",
        "--token",
        type=str,
        default=None,
        help="GitHub Personal Access Token to avoid rate limits (defaults to GITHUB_TOKEN environment variable).",
    )
    return parser


def run(argv: list[str] | None = None) -> int:
    """Run the GitHub Activity CLI command with the given argument list.

    Returns:
        Exit code: 0 on success, 1 on application error, 2 on argument parse error.
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    try:
        events = fetch_user_events(
            username=args.username,
            limit=args.limit,
            token=args.token,
        )
    except (UserNotFoundError, RateLimitExceededError, NetworkError, GitHubAPIError, ValueError) as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    if not events:
        print(f"No recent public activity found for '{args.username}'.")
        return 0

    formatted_lines = format_activities(events)
    for line in formatted_lines:
        print(line)

    return 0


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
