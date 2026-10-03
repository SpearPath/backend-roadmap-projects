"""Event formatting and human-readable representation for GitHub activity."""

from datetime import datetime, timezone


def format_relative_time(iso_timestamp: str, now: datetime | None = None) -> str:
    """Convert an ISO-8601 timestamp string into a friendly relative time description."""
    if not iso_timestamp:
        return "recently"

    try:
        clean_ts = iso_timestamp.replace("Z", "+00:00")
        event_time = datetime.fromisoformat(clean_ts)
        if event_time.tzinfo is None:
            event_time = event_time.replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return "recently"

    current_time = now if now is not None else datetime.now(timezone.utc)
    delta_seconds = max(0, int((current_time - event_time).total_seconds()))

    if delta_seconds < 60:
        return "just now"

    minutes = delta_seconds // 60
    if minutes < 60:
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"

    hours = delta_seconds // 3600
    if hours < 24:
        return f"{hours} hour{'s' if hours != 1 else ''} ago"

    days = delta_seconds // 86400
    if days == 1:
        return "yesterday"
    return f"{days} days ago"


def format_event(event: dict, now: datetime | None = None) -> str:
    """Format a single GitHub event dictionary into a clean, human-readable bullet item."""
    event_type = event.get("type", "Activity")
    repo = event.get("repo", {}).get("name", "unknown/repository")
    created_at = event.get("created_at", "")
    time_str = format_relative_time(created_at, now=now)
    payload = event.get("payload", {})

    if event_type == "PushEvent":
        commits = payload.get("commits", [])
        count = len(commits) if commits else payload.get("size", 1)
        commit_word = "commit" if count == 1 else "commits"
        return f"- Pushed {count} {commit_word} to {repo} ({time_str})"

    if event_type == "IssuesEvent":
        action = payload.get("action", "opened").capitalize()
        issue_num = payload.get("issue", {}).get("number")
        num_str = f" (#{issue_num})" if issue_num is not None else ""
        return f"- {action} an issue in {repo}{num_str} ({time_str})"

    if event_type == "WatchEvent":
        return f"- Starred {repo} ({time_str})"

    if event_type == "ForkEvent":
        forkee = payload.get("forkee", {}).get("full_name")
        target_str = f" to {forkee}" if forkee else ""
        return f"- Forked {repo}{target_str} ({time_str})"

    if event_type == "CreateEvent":
        ref_type = payload.get("ref_type", "resource")
        ref = payload.get("ref")
        if ref:
            return f"- Created {ref_type} '{ref}' in {repo} ({time_str})"
        return f"- Created {ref_type} {repo} ({time_str})"

    if event_type == "DeleteEvent":
        ref_type = payload.get("ref_type", "resource")
        ref = payload.get("ref", "")
        return f"- Deleted {ref_type} '{ref}' in {repo} ({time_str})"

    if event_type == "PullRequestEvent":
        action = payload.get("action", "opened").capitalize()
        pr_num = payload.get("pull_request", {}).get("number")
        num_str = f" #{pr_num}" if pr_num is not None else ""
        return f"- {action} pull request{num_str} in {repo} ({time_str})"

    if event_type == "IssueCommentEvent":
        issue_num = payload.get("issue", {}).get("number")
        num_str = f" #{issue_num}" if issue_num is not None else ""
        return f"- Commented on issue{num_str} in {repo} ({time_str})"

    return f"- {event_type} in {repo} ({time_str})"


def format_activities(
    events: list[dict], limit: int | None = None, now: datetime | None = None
) -> list[str]:
    """Format a list of GitHub event objects into an ordered list of strings."""
    selected_events = events[:limit] if limit is not None else events
    return [format_event(event, now=now) for event in selected_events]
