from datetime import datetime
import storage


def add_tasks(description: str) -> dict:
    tasks = storage.load_tasks()

    # 1. Calculate auto-increment ID
    new_id = max([task["id"] for task in tasks], default=0) + 1

    # 2. Timestamp
    now = datetime.now().isoformat()

    # 3. Create task object
    new_task = {
        "id": new_id,
        "description": description.strip(),
        "status": "todo",
        "created_at": now,
        "updated_at": now,
    }

    # 4. Append and persist
    tasks.append(new_task)
    storage.save_tasks(tasks)
    return new_task


def list_tasks(status: str | None = None) -> list[dict]:
    tasks = storage.load_tasks()
    if status is None:
        return tasks
    return [task for task in tasks if task["status"] == status]


def update_tasks(
    task_id: int,
    new_description: str | None = None,
    new_status: str | None = None,
) -> dict | None:
    tasks = storage.load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            if new_description is not None:
                task["description"] = new_description.strip()
            if new_status is not None:
                task["status"] = new_status
            task["updated_at"] = datetime.now().isoformat()
            storage.save_tasks(tasks)
            return task
    return None


def mark_status(task_id: int, new_status: str) -> dict | None:
    tasks = storage.load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["status"] = new_status
            task["updated_at"] = datetime.now().isoformat()
            storage.save_tasks(tasks)
            return task
    return None


def delete_task(task_id: int) -> bool:
    tasks = storage.load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            storage.save_tasks(tasks)
            return True
    return False


if __name__ == "__main__":
    task1 = add_tasks("First test task")
    print("Created:", task1)