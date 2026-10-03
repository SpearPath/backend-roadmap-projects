import json
import os
import unittest
from pathlib import Path
import storage

class TestStorage(unittest.TestCase):
    def setUp(self):
        self.test_file = Path("temp_tasks.json")
        storage.FILE_PATH = self.test_file

        if self.test_file.exists():
            self.test_file.unlink()
    
    def tearDown(self):
        if self.test_file.exists():
            self.test_file.unlink()
    
    def test_load_tasks_empty_when_file_missing(self):
        tasks = storage.load_tasks()
        self.assertEqual(tasks, [])
    
    def test_save_and_load_task(self):
        tasks = [{"id": 1, "title": "Test", "completed": False}]
        storage.save_tasks(tasks)
        loaded_tasks = storage.load_tasks()
        self.assertEqual(loaded_tasks, tasks)
    
    def test_load_tasks_with_existing_data(self):
        tasks = [{"id": 1, "title": "Test", "completed": False}]
        with open(self.test_file, "w") as f:
            json.dump(tasks, f)
        loaded_tasks = storage.load_tasks()
        self.assertEqual(loaded_tasks, tasks)

    def test_load_tasks_corrupted_json(self):
        """Ensure malformed JSON is handled gracefully by returning empty list."""
        self.test_file.write_text("{ not valid json: ")
        self.assertEqual(storage.load_tasks(), [])

    def test_load_tasks_empty_file(self):
        """Ensure an empty 0-byte file returns empty list rather than crashing."""
        self.test_file.write_text("")
        self.assertEqual(storage.load_tasks(), [])

    def test_save_tasks_overwrites_existing_content(self):
        """Ensure saving new tasks completely overwrites previous data rather than appending."""
        initial = [{"id": 1, "title": "Old", "completed": False}]
        updated = [{"id": 2, "title": "New", "completed": True}]
        storage.save_tasks(initial)
        storage.save_tasks(updated)
        self.assertEqual(storage.load_tasks(), updated)
    
if __name__ == '__main__':
    unittest.main()