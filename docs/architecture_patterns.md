# Backend Architecture Patterns & Principles

## 1. Separation of Concerns (Layered Architecture)
- **Presentation / Interface Layer** (`main.py`, CLI commands, FastAPI routers): Handles user input, parses arguments, validates request formatting, returns status codes / output.
- **Service / Business Logic Layer** (`task_manager.py`): Enforces business rules, validation, status transitions, ID generation.
- **Data Access / Persistence Layer** (`storage.py`, ORM/Repository): Reads and writes data to disk, JSON, or SQL database without mixing business logic.

## 2. Decoupling & Dependency Inversion
- Core business logic should never directly depend on low-level UI details (CLI arguments, HTTP headers).
- Keep storage swappable where possible (e.g. JSON file storage today, SQLite database tomorrow).

## 3. Graceful Error Handling
- Never crash on expected edge cases (missing files, malformed JSON, invalid IDs).
- Return explicit error states, raise domain-specific exceptions, or provide clean user feedback.
