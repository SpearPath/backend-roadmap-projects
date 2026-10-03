import io
import json
import unittest
import urllib.error
from unittest.mock import patch, MagicMock

import github_client
from github_client import (
    fetch_user_events,
    GitHubAPIError,
    UserNotFoundError,
    RateLimitExceededError,
    NetworkError,
)


class TestGitHubClient(unittest.TestCase):
    @patch("urllib.request.urlopen")
    def test_fetch_user_events_success(self, mock_urlopen):
        mock_data = [
            {"id": "1", "type": "PushEvent", "repo": {"name": "octocat/Hello-World"}},
            {"id": "2", "type": "WatchEvent", "repo": {"name": "octocat/Spoon-Knife"}},
        ]
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(mock_data).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        events = fetch_user_events("octocat", limit=2)
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["type"], "PushEvent")

        # Verify request parameters
        call_args, _ = mock_urlopen.call_args
        req = call_args[0]
        self.assertIn("users/octocat/events", req.full_url)
        self.assertEqual(req.headers.get("User-agent"), "github-activity-cli")
        self.assertIn("application/vnd.github.v3+json", req.headers.get("Accept", ""))

    @patch("urllib.request.urlopen")
    def test_fetch_user_events_with_token(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b"[]"
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        fetch_user_events("octocat", token="fake_token_123")

        call_args, _ = mock_urlopen.call_args
        req = call_args[0]
        self.assertEqual(req.headers.get("Authorization"), "Bearer fake_token_123")

    @patch("urllib.request.urlopen")
    def test_fetch_user_events_not_found_404(self, mock_urlopen):
        err = urllib.error.HTTPError(
            url="https://api.github.com/users/nonexistent_user/events",
            code=404,
            msg="Not Found",
            hdrs={},
            fp=io.BytesIO(b'{"message": "Not Found"}'),
        )
        mock_urlopen.side_effect = err

        with self.assertRaises(UserNotFoundError) as ctx:
            fetch_user_events("nonexistent_user")
        self.assertIn("nonexistent_user", str(ctx.exception))

    @patch("urllib.request.urlopen")
    def test_fetch_user_events_rate_limited_403(self, mock_urlopen):
        err = urllib.error.HTTPError(
            url="https://api.github.com/users/octocat/events",
            code=403,
            msg="Forbidden",
            hdrs={},
            fp=io.BytesIO(b'{"message": "API rate limit exceeded"}'),
        )
        mock_urlopen.side_effect = err

        with self.assertRaises(RateLimitExceededError):
            fetch_user_events("octocat")

    @patch("urllib.request.urlopen")
    def test_fetch_user_events_generic_http_error(self, mock_urlopen):
        err = urllib.error.HTTPError(
            url="https://api.github.com/users/octocat/events",
            code=500,
            msg="Internal Server Error",
            hdrs={},
            fp=io.BytesIO(b"server error"),
        )
        mock_urlopen.side_effect = err

        with self.assertRaises(GitHubAPIError):
            fetch_user_events("octocat")

    @patch("urllib.request.urlopen")
    def test_fetch_user_events_network_error(self, mock_urlopen):
        err = urllib.error.URLError("Connection refused")
        mock_urlopen.side_effect = err

        with self.assertRaises(NetworkError):
            fetch_user_events("octocat")

    @patch("urllib.request.urlopen")
    def test_fetch_user_events_invalid_json(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b"<html>not json</html>"
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        with self.assertRaises(GitHubAPIError):
            fetch_user_events("octocat")


if __name__ == "__main__":
    unittest.main()
