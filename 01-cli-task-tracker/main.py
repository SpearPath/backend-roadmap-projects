import sys
from datetime import datetime
import task_manager

VALID_STATUSES = {"todo", "in-progress", "done"}


def print_help() -> None:
    print(
        """Task Tracker CLI - Manage your tasks from the terminal

Usage:
  task-cli <command> [arguments]
  (or python main.py <command> [arguments])

Commands:
  add "<description>"           Add a new task
  update <id> "<description>"   Update the description of an existing task
  delete <id>                   Delete a task by ID
  mark-in-progress <id>         Set task status to 'in-progress'
  mark-done <id>                Set task status to 'done'
  list                          List all tasks
  list <status>                 List tasks by status (todo, in-progress, done)
  help, --help, -h              Display this help guide
"""
    )



def format_timestamp(iso_str: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return iso_str


def print_task_table(tasks: list[dict], status_filter: str | None = None) -> None:
    if not tasks:
        if status_filter:
            print(f"No tasks found with status '{status_filter}'.")
        else:
            print("No tasks found. Add a new task using: python main.py add \"<description>\"")
        return

    # Print table header
    header = f"{'ID':<6} {'Status':<14} {'Description':<40} {'Updated At':<20}"
    separator = "-" * len(header)
    print(header)
    print(separator)

    for task in tasks:
        task_id = str(task.get("id", ""))
        status = task.get("status", "")
        description = task.get("description", "")
        # Truncate description if too long for display in table
        if len(description) > 37:
            description = description[:34] + "..."
        updated_at = format_timestamp(task.get("updated_at", ""))
        print(f"{task_id:<6} {status:<14} {description:<40} {updated_at:<20}")


def parse_task_id(id_str: str) -> int | None:
    try:
        task_id = int(id_str)
        if task_id <= 0:
            return None
        return task_id
    except ValueError:
        return None


def handle_add(args: list[str]) -> int:
    if not args:
        print("Error: Missing task description.")
        print("Usage: python main.py add \"<description>\"")
        return 1

    description = " ".join(args).strip()
    if not description:
        print("Error: Task description cannot be empty.")
        return 1

    new_task = task_manager.add_tasks(description)
    print(f"Task added successfully (ID: {new_task['id']})")
    return 0


def handle_update(args: list[str]) -> int:
    if len(args) < 2:
        print("Error: Both task ID and new description are required.")
        print("Usage: python main.py update <id> \"<new description>\"")
        return 1

    task_id = parse_task_id(args[0])
    if task_id is None:
        print(f"Error: Invalid task ID '{args[0]}'. Must be a positive integer.")
        return 1

    new_description = " ".join(args[1:]).strip()
    if not new_description:
        print("Error: New task description cannot be empty.")
        return 1

    updated = task_manager.update_tasks(task_id, new_description=new_description)
    if updated is None:
        print(f"Error: Task with ID {task_id} not found.")
        return 1

    print(f"Task updated successfully (ID: {task_id})")
    return 0


def handle_delete(args: list[str]) -> int:
    if not args:
        print("Error: Missing task ID.")
        print("Usage: python main.py delete <id>")
        return 1

    task_id = parse_task_id(args[0])
    if task_id is None:
        print(f"Error: Invalid task ID '{args[0]}'. Must be a positive integer.")
        return 1

    deleted = task_manager.delete_task(task_id)
    if not deleted:
        print(f"Error: Task with ID {task_id} not found.")
        return 1

    print(f"Task deleted successfully (ID: {task_id})")
    return 0


def handle_mark_status(args: list[str], status: str) -> int:
    if not args:
        print("Error: Missing task ID.")
        print(f"Usage: python main.py mark-{status} <id>")
        return 1

    task_id = parse_task_id(args[0])
    if task_id is None:
        print(f"Error: Invalid task ID '{args[0]}'. Must be a positive integer.")
        return 1

    updated = task_manager.mark_status(task_id, status)
    if updated is None:
        print(f"Error: Task with ID {task_id} not found.")
        return 1

    print(f"Task marked as {status} (ID: {task_id})")
    return 0


def handle_list(args: list[str]) -> int:
    status_filter = None
    if args:
        status_filter = args[0].lower().strip()
        if status_filter not in VALID_STATUSES:
            print(
                f"Error: Invalid status '{status_filter}'. Allowed: {', '.join(sorted(VALID_STATUSES))}"
            )
            return 1

    tasks = task_manager.list_tasks(status=status_filter)
    print_task_table(tasks, status_filter)
    return 0


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if not argv or argv[0] in ("-h", "--help", "help"):
        print_help()
        return 0

    command = argv[0].lower().strip()
    args = argv[1:]

    if command == "add":
        return handle_add(args)
    elif command == "update":
        return handle_update(args)
    elif command == "delete":
        return handle_delete(args)
    elif command == "mark-in-progress":
        return handle_mark_status(args, "in-progress")
    elif command == "mark-done":
        return handle_mark_status(args, "done")
    elif command == "list":
        return handle_list(args)
    else:
        print(f"Error: Unknown command '{argv[0]}'.")
        print("Run 'python main.py help' to see available commands.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
