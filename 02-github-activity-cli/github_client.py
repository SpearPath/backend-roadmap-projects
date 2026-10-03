"""HTTP client module for fetching user activity from the GitHub REST API using urllib."""

import json
import os
import urllib.error
import urllib.parse
import urllib.request


class GitHubAPIError(Exception):
    """Base exception for all GitHub API client errors."""


class UserNotFoundError(GitHubAPIError):
    """Raised when the specified user does not exist (HTTP 404)."""


class RateLimitExceededError(GitHubAPIError):
    """Raised when GitHub API rate limit is exceeded (HTTP 403)."""


class NetworkError(GitHubAPIError):
    """Raised when network connectivity fails or times out."""


def fetch_user_events(
    username: str, limit: int = 10, token: str | None = None
) -> list[dict]:
    """Fetch recent public events for a GitHub user.

    Args:
        username: GitHub username.
        limit: Maximum number of events to fetch/return.
        token: Optional personal access token (falls back to GITHUB_TOKEN environment variable).

    Returns:
        A list of event dictionaries returned by GitHub.

    Raises:
        UserNotFoundError: If the user is not found on GitHub (404).
        RateLimitExceededError: If the API rate limit is exceeded (403).
        NetworkError: If a connection or DNS error occurs.
        GitHubAPIError: For other HTTP errors or malformed responses.
    """
    clean_username = username.strip()
    if not clean_username:
        raise ValueError("Username cannot be empty.")

    page_size = max(1, min(limit, 100))
    encoded_username = urllib.parse.quote(clean_username)
    url = f"https://api.github.com/users/{encoded_username}/events?per_page={page_size}"

    headers = {
        "User-Agent": "github-activity-cli",
        "Accept": "application/vnd.github.v3+json",
    }

    auth_token = token or os.environ.get("GITHUB_TOKEN")
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=10.0) as response:
            raw_body = response.read()
            data = json.loads(raw_body.decode("utf-8"))
            if not isinstance(data, list):
                raise GitHubAPIError("Unexpected response format received from GitHub.")
            return data[:limit]
    except urllib.error.HTTPError as err:
        if err.code == 404:
            raise UserNotFoundError(f"User '{clean_username}' not found on GitHub.") from err
        if err.code == 403:
            raise RateLimitExceededError(
                "GitHub API rate limit exceeded. Set a GITHUB_TOKEN environment variable or use --token to increase limits."
            ) from err
        raise GitHubAPIError(f"GitHub API error (HTTP {err.code}): {err.reason}") from err
    except urllib.error.URLError as err:
        raise NetworkError(f"Network error connecting to GitHub: {err.reason}") from err
    except json.JSONDecodeError as err:
        raise GitHubAPIError(f"Failed to parse GitHub JSON response: {err}") from err
