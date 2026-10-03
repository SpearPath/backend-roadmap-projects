# GitHub User Activity CLI

A lightweight, zero-dependency command-line interface (CLI) to fetch and display the recent public activity of any GitHub user in your terminal.

Built as part of the [roadmap.sh Backend Developer Roadmap (Project 02: GitHub User Activity)](https://roadmap.sh/projects/github-user-activity).

---

## Features

- **Zero External Dependencies**: Built entirely using the Python standard library (`urllib.request`, `json`, `argparse`, `datetime`).
- **Human-Friendly Event Summaries**: Formats raw GitHub events into clear, natural language actions.
- **Relative Timestamps**: Displays intuitive elapsed times (e.g. `just now`, `15 minutes ago`, `2 hours ago`, `yesterday`, `5 days ago`).
- **Comprehensive Event Support**:
  - `PushEvent`: Number of commits and target repository
  - `IssuesEvent`: Opened, closed, or reopened issues with issue numbers
  - `WatchEvent`: Starred repositories
  - `ForkEvent`: Forked repositories and target destinations
  - `CreateEvent`: Created repositories, branches, or tags
  - `DeleteEvent`: Deleted branches or tags
  - `PullRequestEvent`: PR actions and numbers
  - `IssueCommentEvent`: Comments on issues
- **Rate Limit Protection**: Supports authentication via `--token` or the `GITHUB_TOKEN` environment variable to increase GitHub API limits from 60 to 5,000 requests/hour.
- **Robust Error Handling**: Dedicated domain exceptions and user-friendly messages for missing users (404), rate limiting (403), network outages, and users with zero recent activity.
- **Full Test Coverage**: Comprehensive test suite with 100% mock coverage for fast, offline-capable unit testing.

---

## Project Structure

```text
02-github-activity-cli/
│
├── README.md                      # Documentation & usage guide
├── github_client.py               # HTTP networking, headers, auth token, and domain exceptions
├── formatter.py                   # Event parsing, human-readable strings, relative timestamps
├── main.py                        # CLI entry point, argument parsing, error formatting
│
└── tests/
    ├── __init__.py
    ├── test_formatter.py          # Unit tests for relative time & event type parsing (18 tests)
    ├── test_github_client.py      # Mocked unit tests for HTTP 200, 404, 403, and network errors (7 tests)
    └── test_cli.py                # Unit tests for argument parsing and CLI flow (6 tests)
```

---

## Installation & Requirements

- **Python**: Version 3.10+ (tested with Python 3.13)
- **External packages**: None required.

---

## Usage

### Direct CLI (Windows Batch Wrapper)
```cmd
github-activity <username>
```
Or with explicit script execution:
```bash
python main.py <username>
```

### Examples

#### 1. Basic user query
```bash
python main.py torvalds
```
**Output:**
```text
- Pushed 1 commit to torvalds/linux (10 hours ago)
- Pushed 1 commit to torvalds/GuitarPedal (12 hours ago)
- Pushed 1 commit to torvalds/linux (14 hours ago)
- Pushed 1 commit to torvalds/GuitarPedal (14 hours ago)
- Pushed 1 commit to torvalds/GuitarPedal (2 days ago)
```

#### 2. Limit the number of events
Use the `-n` or `--limit` flag:
```bash
python main.py kamranahmedse --limit 3
```

#### 3. Using a GitHub Personal Access Token
Unauthenticated requests to the GitHub API are limited to 60 per hour per IP. To authenticate:

**Via command line flag:**
```bash
python main.py <username> --token "ghp_yourPersonalAccessToken"
```

**Via environment variable:**
```bash
# PowerShell
$env:GITHUB_TOKEN = "ghp_yourPersonalAccessToken"
python main.py <username>

# Bash / Zsh
export GITHUB_TOKEN="ghp_yourPersonalAccessToken"
python main.py <username>
```

---

## CLI Reference

```text
usage: github-activity [-h] [-n LIMIT] [-t TOKEN] username

Fetch and display the recent public activity of a specified GitHub user.

positional arguments:
  username           GitHub username to fetch activity for.

options:
  -h, --help         show this help message and exit
  -n, --limit LIMIT  Maximum number of events to display (default: 10).
  -t, --token TOKEN  GitHub Personal Access Token to avoid rate limits
                     (defaults to GITHUB_TOKEN environment variable).
```

### Exit Codes

| Code | Meaning |
| :---: | :--- |
| `0` | Success (events displayed, or user had no recent activity) |
| `1` | Operational error (user not found, rate limit exceeded, network down) |
| `2` | Command invocation error (missing username or invalid flags) |

---

## Running Unit Tests

All unit tests use `unittest.mock` to simulate GitHub API responses, ensuring fast, deterministic, and fully offline execution without consuming your GitHub API quota.

Run the entire test suite from the project directory:

```bash
python -m unittest discover tests
```

Run specific test modules:

```bash
python -m unittest tests/test_formatter.py
python -m unittest tests/test_github_client.py
python -m unittest tests/test_cli.py
```
