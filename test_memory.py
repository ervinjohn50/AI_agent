import unittest
import os
import json
import shutil
import tempfile
from memory import load_memory, save_memory, format_memory_for_prompt


class TestMemory(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_load_memory_empty_when_no_file(self):
        result = load_memory(self.test_dir)
        self.assertEqual(result, [])

    def test_save_and_load_memory(self):
        save_memory(self.test_dir, "fix the bug", "Fixed a typo on line 5", ["get_file_content", "write_file"])
        history = load_memory(self.test_dir)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["prompt"], "fix the bug")
        self.assertEqual(history[0]["result"], "Fixed a typo on line 5")
        self.assertEqual(history[0]["tools_used"], ["get_file_content", "write_file"])

    def test_memory_appends_across_sessions(self):
        save_memory(self.test_dir, "first prompt", "first result", ["get_files_info"])
        save_memory(self.test_dir, "second prompt", "second result", ["search_files"])
        history = load_memory(self.test_dir)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["prompt"], "first prompt")
        self.assertEqual(history[1]["prompt"], "second prompt")

    def test_memory_caps_at_max_history(self):
        for i in range(15):
            save_memory(self.test_dir, f"prompt {i}", f"result {i}", [])
        history = load_memory(self.test_dir)
        self.assertEqual(len(history), 10)
        self.assertEqual(history[0]["prompt"], "prompt 5")
        self.assertEqual(history[-1]["prompt"], "prompt 14")

    def test_load_memory_handles_corrupt_file(self):
        memory_dir = os.path.join(self.test_dir, ".agent_memory")
        os.makedirs(memory_dir)
        with open(os.path.join(memory_dir, "history.json"), "w") as f:
            f.write("not valid json{{{")
        result = load_memory(self.test_dir)
        self.assertEqual(result, [])

    def test_format_memory_empty(self):
        result = format_memory_for_prompt([])
        self.assertEqual(result, "")

    def test_format_memory_includes_entries(self):
        history = [
            {
                "timestamp": "2026-08-01T12:00:00",
                "prompt": "fix the tests",
                "result": "Fixed assertion error in test_calc.py",
                "tools_used": ["search_files", "write_file"],
            }
        ]
        result = format_memory_for_prompt(history)
        self.assertIn("fix the tests", result)
        self.assertIn("Fixed assertion error", result)
        self.assertIn("search_files", result)


if __name__ == "__main__":
    unittest.main()
