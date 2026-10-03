import io
import unittest
from pathlib import Path
from unittest.mock import patch
import storage
import main


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.test_file = Path("temp_test_cli_tasks.json")
        storage.FILE_PATH = self.test_file
        if self.test_file.exists():
            self.test_file.unlink()

    def tearDown(self):
        if self.test_file.exists():
            self.test_file.unlink()

    def run_cli(self, argv: list[str]) -> tuple[int, str]:
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            exit_code = main.main(argv)
            return exit_code, mock_stdout.getvalue()

    def test_help_no_args(self):
        code, out = self.run_cli([])
        self.assertEqual(code, 0)
        self.assertIn("Task Tracker CLI", out)

    def test_help_flag(self):
        code, out = self.run_cli(["--help"])
        self.assertEqual(code, 0)
        self.assertIn("Task Tracker CLI", out)

    def test_add_success(self):
        code, out = self.run_cli(["add", "Buy milk"])
        self.assertEqual(code, 0)
        self.assertIn("Task added successfully (ID: 1)", out)

        tasks = storage.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["description"], "Buy milk")

    def test_add_missing_description(self):
        code, out = self.run_cli(["add"])
        self.assertEqual(code, 1)
        self.assertIn("Error: Missing task description.", out)

    def test_update_success(self):
        self.run_cli(["add", "Original task"])
        code, out = self.run_cli(["update", "1", "Updated task"])
        self.assertEqual(code, 0)
        self.assertIn("Task updated successfully (ID: 1)", out)

        tasks = storage.load_tasks()
        self.assertEqual(tasks[0]["description"], "Updated task")

    def test_update_nonexistent_id(self):
        code, out = self.run_cli(["update", "999", "Does not exist"])
        self.assertEqual(code, 1)
        self.assertIn("Error: Task with ID 999 not found.", out)

    def test_update_invalid_id(self):
        code, out = self.run_cli(["update", "abc", "Some task"])
        self.assertEqual(code, 1)
        self.assertIn("Error: Invalid task ID 'abc'", out)

    def test_mark_in_progress(self):
        self.run_cli(["add", "Task to progress"])
        code, out = self.run_cli(["mark-in-progress", "1"])
        self.assertEqual(code, 0)
        self.assertIn("Task marked as in-progress (ID: 1)", out)

        tasks = storage.load_tasks()
        self.assertEqual(tasks[0]["status"], "in-progress")

    def test_mark_done(self):
        self.run_cli(["add", "Task to complete"])
        code, out = self.run_cli(["mark-done", "1"])
        self.assertEqual(code, 0)
        self.assertIn("Task marked as done (ID: 1)", out)

        tasks = storage.load_tasks()
        self.assertEqual(tasks[0]["status"], "done")

    def test_delete_success(self):
        self.run_cli(["add", "Task to delete"])
        code, out = self.run_cli(["delete", "1"])
        self.assertEqual(code, 0)
        self.assertIn("Task deleted successfully (ID: 1)", out)

        tasks = storage.load_tasks()
        self.assertEqual(len(tasks), 0)

    def test_delete_nonexistent(self):
        code, out = self.run_cli(["delete", "999"])
        self.assertEqual(code, 1)
        self.assertIn("Error: Task with ID 999 not found.", out)

    def test_list_all(self):
        self.run_cli(["add", "Task 1"])
        self.run_cli(["add", "Task 2"])
        code, out = self.run_cli(["list"])
        self.assertEqual(code, 0)
        self.assertIn("Task 1", out)
        self.assertIn("Task 2", out)
        self.assertIn("ID", out)
        self.assertIn("Status", out)

    def test_list_filtered(self):
        self.run_cli(["add", "Task Todo"])
        self.run_cli(["add", "Task Done"])
        self.run_cli(["mark-done", "2"])

        code, out = self.run_cli(["list", "done"])
        self.assertEqual(code, 0)
        self.assertIn("Task Done", out)
        self.assertNotIn("Task Todo", out)

    def test_list_invalid_status(self):
        code, out = self.run_cli(["list", "invalid_status"])
        self.assertEqual(code, 1)
        self.assertIn("Error: Invalid status 'invalid_status'", out)

    def test_unknown_command(self):
        code, out = self.run_cli(["unknown_cmd"])
        self.assertEqual(code, 1)
        self.assertIn("Error: Unknown command 'unknown_cmd'", out)


if __name__ == "__main__":
    unittest.main()
