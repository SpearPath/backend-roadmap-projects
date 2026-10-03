import unittest
from pathlib import Path
from datetime import datetime
import storage
import task_manager


class TestTaskManager(unittest.TestCase):
    def setUp(self):
        self.test_file = Path("temp_test_tasks.json")
        storage.FILE_PATH = self.test_file

        if self.test_file.exists():
            self.test_file.unlink()

    def tearDown(self):
        if self.test_file.exists():
            self.test_file.unlink()

    def test_add_task_creates_valid_task(self):
        """Verify task creation with proper fields, default status, and trimmed description."""
        task = task_manager.add_tasks("  Buy groceries  ")

        self.assertEqual(task["id"], 1)
        self.assertEqual(task["description"], "Buy groceries")
        self.assertEqual(task["status"], "todo")
        self.assertIsNotNone(task.get("created_at"))
        self.assertIsNotNone(task.get("updated_at"))
        # Verify valid ISO datetime format
        datetime.fromisoformat(task["created_at"])
        datetime.fromisoformat(task["updated_at"])

        # Verify task is persisted
        stored_tasks = storage.load_tasks()
        self.assertEqual(len(stored_tasks), 1)
        self.assertEqual(stored_tasks[0], task)

    def test_add_tasks_incremental_ids(self):
        """Verify task IDs auto-increment sequentially."""
        task1 = task_manager.add_tasks("Task 1")
        task2 = task_manager.add_tasks("Task 2")
        task3 = task_manager.add_tasks("Task 3")

        self.assertEqual(task1["id"], 1)
        self.assertEqual(task2["id"], 2)
        self.assertEqual(task3["id"], 3)

    def test_add_tasks_after_deletion_calculates_correct_next_id(self):
        """Ensure new ID is max(existing_ids) + 1 even if earlier tasks are deleted."""
        task_manager.add_tasks("Task 1")
        task_manager.add_tasks("Task 2")
        task_manager.delete_task(1)

        task3 = task_manager.add_tasks("Task 3")
        self.assertEqual(task3["id"], 3)

    def test_list_tasks_empty(self):
        """Verify list_tasks returns an empty list when no tasks exist."""
        self.assertEqual(task_manager.list_tasks(), [])

    def test_list_tasks_all(self):
        """Verify list_tasks returns all saved tasks."""
        task_manager.add_tasks("Task A")
        task_manager.add_tasks("Task B")

        all_tasks = task_manager.list_tasks()
        self.assertEqual(len(all_tasks), 2)
        self.assertEqual(all_tasks[0]["description"], "Task A")
        self.assertEqual(all_tasks[1]["description"], "Task B")

    def test_list_tasks_by_status(self):
        """Verify list_tasks filtering by status."""
        task_manager.add_tasks("Task Todo")
        t2 = task_manager.add_tasks("Task In Progress")
        t3 = task_manager.add_tasks("Task Done")

        task_manager.mark_status(t2["id"], "in-progress")
        task_manager.mark_status(t3["id"], "done")

        todo_tasks = task_manager.list_tasks(status="todo")
        self.assertEqual(len(todo_tasks), 1)
        self.assertEqual(todo_tasks[0]["description"], "Task Todo")

        in_progress_tasks = task_manager.list_tasks(status="in-progress")
        self.assertEqual(len(in_progress_tasks), 1)
        self.assertEqual(in_progress_tasks[0]["description"], "Task In Progress")

        done_tasks = task_manager.list_tasks(status="done")
        self.assertEqual(len(done_tasks), 1)
        self.assertEqual(done_tasks[0]["description"], "Task Done")

        nonexistent_status = task_manager.list_tasks(status="archived")
        self.assertEqual(nonexistent_status, [])

    def test_update_tasks_description_only(self):
        """Verify updating only task description."""
        task = task_manager.add_tasks("Original description")
        updated = task_manager.update_tasks(task["id"], new_description="Updated description")

        self.assertIsNotNone(updated)
        self.assertEqual(updated["description"], "Updated description")
        self.assertEqual(updated["status"], "todo")
        self.assertGreaterEqual(updated["updated_at"], task["created_at"])

        # Check storage reflection
        stored = storage.load_tasks()[0]
        self.assertEqual(stored["description"], "Updated description")

    def test_update_tasks_status_only(self):
        """Verify updating only task status."""
        task = task_manager.add_tasks("My task")
        updated = task_manager.update_tasks(task["id"], new_status="done")

        self.assertIsNotNone(updated)
        self.assertEqual(updated["description"], "My task")
        self.assertEqual(updated["status"], "done")

    def test_update_tasks_both_description_and_status(self):
        """Verify updating both description and status at the same time."""
        task = task_manager.add_tasks("My task")
        updated = task_manager.update_tasks(
            task["id"],
            new_description="Brand new description",
            new_status="in-progress",
        )

        self.assertIsNotNone(updated)
        self.assertEqual(updated["description"], "Brand new description")
        self.assertEqual(updated["status"], "in-progress")

    def test_update_tasks_nonexistent_id(self):
        """Verify updating a non-existent task returns None."""
        result = task_manager.update_tasks(999, new_description="Ghost task")
        self.assertIsNone(result)

    def test_mark_status(self):
        """Verify mark_status properly sets status and updates timestamp."""
        task = task_manager.add_tasks("Mark test")

        marked_in_progress = task_manager.mark_status(task["id"], "in-progress")
        self.assertIsNotNone(marked_in_progress)
        self.assertEqual(marked_in_progress["status"], "in-progress")

        marked_done = task_manager.mark_status(task["id"], "done")
        self.assertIsNotNone(marked_done)
        self.assertEqual(marked_done["status"], "done")

    def test_mark_status_nonexistent_id(self):
        """Verify mark_status on non-existent task returns None."""
        result = task_manager.mark_status(999, "done")
        self.assertIsNone(result)

    def test_delete_task_success(self):
        """Verify deleting an existing task removes it and returns True."""
        t1 = task_manager.add_tasks("Task 1")
        t2 = task_manager.add_tasks("Task 2")

        deleted = task_manager.delete_task(t1["id"])
        self.assertTrue(deleted)

        remaining = task_manager.list_tasks()
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0]["id"], t2["id"])

    def test_delete_task_nonexistent_id(self):
        """Verify deleting a non-existent task returns False and leaves tasks intact."""
        task_manager.add_tasks("Task 1")
        deleted = task_manager.delete_task(999)

        self.assertFalse(deleted)
        self.assertEqual(len(task_manager.list_tasks()), 1)


if __name__ == "__main__":
    unittest.main()
