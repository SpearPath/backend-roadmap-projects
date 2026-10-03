import io
import unittest
from unittest.mock import patch

import main
from github_client import UserNotFoundError, RateLimitExceededError, NetworkError, GitHubAPIError


class TestCLI(unittest.TestCase):
    @patch("main.fetch_user_events")
    def test_cli_success_with_events(self, mock_fetch):
        mock_fetch.return_value = [
            {
                "type": "PushEvent",
                "repo": {"name": "octocat/Hello-World"},
                "created_at": "2026-10-03T10:00:00Z",
                "payload": {"size": 2, "commits": [{"message": "c1"}, {"message": "c2"}]},
            }
        ]

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            exit_code = main.run(["octocat"])
            self.assertEqual(exit_code, 0)
            output = mock_stdout.getvalue()
            self.assertIn("Pushed 2 commits to octocat/Hello-World", output)

    @patch("main.fetch_user_events")
    def test_cli_zero_events(self, mock_fetch):
        mock_fetch.return_value = []

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            exit_code = main.run(["octocat"])
            self.assertEqual(exit_code, 0)
            self.assertIn("No recent public activity found for 'octocat'.", mock_stdout.getvalue())

    @patch("main.fetch_user_events")
    def test_cli_user_not_found(self, mock_fetch):
        mock_fetch.side_effect = UserNotFoundError("User 'nobody' not found on GitHub.")

        with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
            exit_code = main.run(["nobody"])
            self.assertEqual(exit_code, 1)
            self.assertIn("User 'nobody' not found", mock_stderr.getvalue())

    @patch("main.fetch_user_events")
    def test_cli_rate_limit(self, mock_fetch):
        mock_fetch.side_effect = RateLimitExceededError("Rate limit exceeded")

        with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
            exit_code = main.run(["octocat"])
            self.assertEqual(exit_code, 1)
            self.assertIn("rate limit exceeded", mock_stderr.getvalue().lower())

    @patch("main.fetch_user_events")
    def test_cli_network_error(self, mock_fetch):
        mock_fetch.side_effect = NetworkError("Network error connecting to GitHub: Connection failed")

        with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
            exit_code = main.run(["octocat"])
            self.assertEqual(exit_code, 1)
            self.assertIn("network error", mock_stderr.getvalue().lower())

    @patch("main.fetch_user_events")
    def test_cli_flags_forwarded(self, mock_fetch):
        mock_fetch.return_value = []
        with patch("sys.stdout"):
            main.run(["octocat", "--limit", "5", "--token", "custom_secret"])
        mock_fetch.assert_called_once_with(username="octocat", limit=5, token="custom_secret")


if __name__ == "__main__":
    unittest.main()
