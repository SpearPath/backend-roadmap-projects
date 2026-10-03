# Backend Engineering Roadmap Projects

A progressive portfolio of backend systems and CLI tools built following the [roadmap.sh backend track](https://roadmap.sh/backend).

## Project Progress

| # | Project Name | Focus Concepts | Language / Tools | Status |
|---|--------------|----------------|------------------|--------|
| 01 | [CLI Task Tracker](./01-cli-task-tracker/) | File I/O, JSON serialization, modular architecture, CLI parsing | Python (Standard Library) | Completed |
| 02 | [GitHub Activity CLI](./02-github-activity-cli/) | REST endpoints, outbound HTTP calls, error boundaries | Python (`urllib` / `httpx`) | Up Next |
| 03 | Expense Tracker API | REST API, CRUD endpoints, SQLite/MySQL persistence | Python (FastAPI) | Planned |
| 04 | URL Shortener Service | Hashing/Base62, redirect semantics, Redis caching | Python / Redis | Planned |

## Running Tests
Run unit tests across any specific project folder:
```bash
python -m unittest discover -s 01-cli-task-tracker/tests
```

## Structure Overview
```text
backend-roadmap/
│
├── .gitignore                      # Root ignore for all projects
├── README.md                       # Master tracking index & roadmap progress
│
├── 01-cli-task-tracker/            # Project 1 (Pure Python / Zero external dependencies)
│   ├── README.md                   # Project documentation & usage
│   ├── storage.py
│   ├── task_manager.py
│   ├── main.py
│   ├── tasks.json
│   └── tests/
│       ├── test_storage.py
│       └── test_task_manager.py
│
├── 02-github-activity-cli/         # Project 2 (HTTP client / external API calls)
│   ├── README.md
│   └── ...
│
├── 03-expense-tracker-api/         # Project 3 (FastAPI / SQLite / relational data)
│   ├── pyproject.toml / requirements.txt
│   ├── README.md
│   └── ...
│
└── docs/                           # Architecture notes & reference cheatsheets
    ├── architecture_patterns.md
    └── rest_and_database_rules.md
```
