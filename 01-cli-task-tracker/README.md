# Project 01: CLI Task Tracker

A lightweight, zero-dependency command line interface (CLI) to track and manage your daily tasks, built with Python standard library.

- Project URL: https://roadmap.sh/projects/task-tracker
- Designed according to the [roadmap.sh Task Tracker project specification](https://roadmap.sh/projects/task-tracker).

---

## Architecture & Design

This project demonstrates a clean **Layered Architecture** with distinct separation of concerns:

```text
01-cli-task-tracker/
├── main.py              # Presentation Layer: CLI parsing & table formatting
├── task_manager.py      # Business Logic Layer: CRUD operations, validation & auto-increment IDs
├── storage.py           # Persistence Layer: JSON file I/O & corruption recovery
├── tasks.json           # Data Store (JSON file)
└── tests/               # Test Suite (unittest)
    ├── test_storage.py
    ├── test_task_manager.py
    └── test_cli.py
```

- **Persistence Layer (`storage.py`)**: Responsible solely for loading and dumping tasks to disk. Safely handles missing files, empty (0-byte) files, and malformed JSON.
- **Service Layer (`task_manager.py`)**: Enforces business logic (generating monotonic IDs, managing ISO timestamps, status updates) without knowing anything about CLI formatting.
- **Presentation Layer (`main.py`)**: Command line parser, user feedback, and tabular terminal rendering.

---

## Features

- **Add Tasks**: Auto-increments unique IDs and timestamps tasks in ISO 8601 format.
- **Update Tasks**: Modify descriptions with automatic `updated_at` timestamp refresh.
- **Delete Tasks**: Remove tasks cleanly while preserving ID sequences.
- **Status Workflow**: Transition tasks smoothly between `todo`, `in-progress`, and `done`.
- **Filtered Listing**: View all tasks or filter dynamically by status in a formatted table.
- **Resilient Persistence**: Survives missing files and JSON errors gracefully.

---

## Usage

You can use either `task-cli` (via `task-cli.bat` on Windows) or `python main.py`:

### 1. Adding a Task
```bash
task-cli add "Buy groceries"
# Output: Task added successfully (ID: 1)
```

### 2. Updating a Task
```bash
python main.py update 1 "Buy groceries and prepare dinner"
# Output: Task updated successfully (ID: 1)
```

### 3. Updating Status
```bash
# Mark as in-progress
python main.py mark-in-progress 1
# Output: Task marked as in-progress (ID: 1)

# Mark as done
python main.py mark-done 1
# Output: Task marked as done (ID: 1)
```

### 4. Listing Tasks
```bash
# List all tasks
python main.py list

# List by status
python main.py list todo
python main.py list in-progress
python main.py list done
```

Output format:
```text
ID     Status         Description                              Updated At          
-----------------------------------------------------------------------------------
1      in-progress    Buy groceries and prepare dinner         2026-10-03 14:15:00 
```

### 5. Deleting a Task
```bash
python main.py delete 1
# Output: Task deleted successfully (ID: 1)
```

### 6. Help
```bash
python main.py help
# or python main.py --help
```

---

## Running Unit Tests

Run all unit tests across the storage, business logic, and CLI layers:

```bash
python -m unittest discover tests
```

To run a specific test suite:
```bash
python -m unittest tests/test_storage.py
python -m unittest tests/test_task_manager.py
python -m unittest tests/test_cli.py
```

---

## Data Schema (`tasks.json`)

Each task is stored as a JSON object:

```json
[
  {
    "id": 1,
    "description": "Buy groceries",
    "status": "todo",
    "created_at": "2026-10-03T13:13:33.044749",
    "updated_at": "2026-10-03T13:13:33.044749"
  }
]
```
