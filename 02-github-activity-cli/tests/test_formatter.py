import unittest
from datetime import datetime, timezone, timedelta
import formatter


class TestFormatter(unittest.TestCase):
    def setUp(self):
        # Fixed reference point for deterministic relative time tests
        self.now = datetime(2026, 10, 3, 12, 0, 0, tzinfo=timezone.utc)

    def test_relative_time_just_now(self):
        ts = (self.now - timedelta(seconds=25)).isoformat()
        self.assertEqual(formatter.format_relative_time(ts, now=self.now), "just now")

    def test_relative_time_minutes_ago(self):
        ts_single = (self.now - timedelta(minutes=1)).isoformat()
        ts_multi = (self.now - timedelta(minutes=15)).isoformat()
        self.assertEqual(formatter.format_relative_time(ts_single, now=self.now), "1 minute ago")
        self.assertEqual(formatter.format_relative_time(ts_multi, now=self.now), "15 minutes ago")

    def test_relative_time_hours_ago(self):
        ts_single = (self.now - timedelta(hours=1)).isoformat()
        ts_multi = (self.now - timedelta(hours=4)).isoformat()
        self.assertEqual(formatter.format_relative_time(ts_single, now=self.now), "1 hour ago")
        self.assertEqual(formatter.format_relative_time(ts_multi, now=self.now), "4 hours ago")

    def test_relative_time_yesterday_and_days(self):
        ts_yesterday = (self.now - timedelta(days=1)).isoformat()
        ts_days = (self.now - timedelta(days=5)).isoformat()
        self.assertEqual(formatter.format_relative_time(ts_yesterday, now=self.now), "yesterday")
        self.assertEqual(formatter.format_relative_time(ts_days, now=self.now), "5 days ago")

    def test_relative_time_fallback(self):
        self.assertEqual(formatter.format_relative_time("invalid-time"), "recently")

    def test_format_push_event_multiple_commits(self):
        event = {
            "type": "PushEvent",
            "repo": {"name": "octocat/Hello-World"},
            "created_at": (self.now - timedelta(hours=2)).isoformat(),
            "payload": {
                "size": 3,
                "commits": [{"message": "c1"}, {"message": "c2"}, {"message": "c3"}]
            }
        }
        result = formatter.format_event(event, now=self.now)
        self.assertEqual(result, "- Pushed 3 commits to octocat/Hello-World (2 hours ago)")

    def test_format_push_event_single_commit(self):
        event = {
            "type": "PushEvent",
            "repo": {"name": "octocat/Hello-World"},
            "created_at": (self.now - timedelta(minutes=30)).isoformat(),
            "payload": {
                "size": 1,
                "commits": [{"message": "c1"}]
            }
        }
        result = formatter.format_event(event, now=self.now)
        self.assertEqual(result, "- Pushed 1 commit to octocat/Hello-World (30 minutes ago)")

    def test_format_issues_event(self):
        event = {
            "type": "IssuesEvent",
            "repo": {"name": "octocat/Hello-World"},
            "created_at": (self.now - timedelta(hours=1)).isoformat(),
            "payload": {
                "action": "opened",
                "issue": {"number": 42}
            }
        }
        result = formatter.format_event(event, now=self.now)
        self.assertEqual(result, "- Opened an issue in octocat/Hello-World (#42) (1 hour ago)")

    def test_format_watch_event(self):
        event = {
            "type": "WatchEvent",
            "repo": {"name": "octocat/Hello-World"},
            "created_at": (self.now - timedelta(days=1)).isoformat(),
            "payload": {"action": "started"}
        }
        result = formatter.format_event(event, now=self.now)
        self.assertEqual(result, "- Starred octocat/Hello-World (yesterday)")

    def test_format_fork_event(self):
        event = {
            "type": "ForkEvent",
            "repo": {"name": "octocat/Hello-World"},
            "created_at": (self.now - timedelta(days=2)).isoformat(),
            "payload": {
                "forkee": {"full_name": "developer/Hello-World"}
            }
        }
        result = formatter.format_event(event, now=self.now)
        self.assertEqual(result, "- Forked octocat/Hello-World to developer/Hello-World (2 days ago)")

    def test_format_create_event_branch(self):
        event = {
            "type": "CreateEvent",
            "repo": {"name": "octocat/Hello-World"},
            "created_at": (self.now - timedelta(minutes=10)).isoformat(),
            "payload": {
                "ref_type": "branch",
                "ref": "feature/login"
            }
        }
        result = formatter.format_event(event, now=self.now)
        self.assertEqual(result, "- Created branch 'feature/login' in octocat/Hello-World (10 minutes ago)")

    def test_format_create_event_repo(self):
        event = {
            "type": "CreateEvent",
            "repo": {"name": "octocat/New-Project"},
            "created_at": (self.now - timedelta(days=3)).isoformat(),
            "payload": {
                "ref_type": "repository",
                "ref": None
            }
        }
        result = formatter.format_event(event, now=self.now)
        self.assertEqual(result, "- Created repository octocat/New-Project (3 days ago)")

    def test_format_delete_event(self):
        event = {
            "type": "DeleteEvent",
            "repo": {"name": "octocat/Hello-World"},
            "created_at": (self.now - timedelta(hours=3)).isoformat(),
            "payload": {
                "ref_type": "branch",
                "ref": "old-feature"
            }
        }
        result = formatter.format_event(event, now=self.now)
        self.assertEqual(result, "- Deleted branch 'old-feature' in octocat/Hello-World (3 hours ago)")

    def test_format_pull_request_event(self):
        event = {
            "type": "PullRequestEvent",
            "repo": {"name": "octocat/Hello-World"},
            "created_at": (self.now - timedelta(minutes=5)).isoformat(),
            "payload": {
                "action": "opened",
                "pull_request": {"number": 7}
            }
        }
        result = formatter.format_event(event, now=self.now)
        self.assertEqual(result, "- Opened pull request #7 in octocat/Hello-World (5 minutes ago)")

    def test_format_issue_comment_event(self):
        event = {
            "type": "IssueCommentEvent",
            "repo": {"name": "octocat/Hello-World"},
            "created_at": (self.now - timedelta(hours=5)).isoformat(),
            "payload": {
                "issue": {"number": 12}
            }
        }
        result = formatter.format_event(event, now=self.now)
        self.assertEqual(result, "- Commented on issue #12 in octocat/Hello-World (5 hours ago)")

    def test_format_unknown_event(self):
        event = {
            "type": "ReleaseEvent",
            "repo": {"name": "octocat/Hello-World"},
            "created_at": (self.now - timedelta(hours=1)).isoformat(),
            "payload": {}
        }
        result = formatter.format_event(event, now=self.now)
        self.assertEqual(result, "- ReleaseEvent in octocat/Hello-World (1 hour ago)")

    def test_format_activities_list_and_limit(self):
        events = [
            {
                "type": "WatchEvent",
                "repo": {"name": f"octocat/Repo-{i}"},
                "created_at": self.now.isoformat(),
                "payload": {}
            }
            for i in range(5)
        ]
        results = formatter.format_activities(events, limit=3, now=self.now)
        self.assertEqual(len(results), 3)

    def test_format_activities_empty(self):
        self.assertEqual(formatter.format_activities([]), [])


if __name__ == "__main__":
    unittest.main()
