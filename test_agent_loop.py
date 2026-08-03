import unittest
from unittest.mock import MagicMock, patch
from google.genai import types
from main import generate_content


def make_mock_response(text=None, function_calls=None):
    response = MagicMock()
    response.usage_metadata = MagicMock()
    response.usage_metadata.prompt_token_count = 10
    response.usage_metadata.candidates_token_count = 20

    if text:
        response.text = text
        response.function_calls = None
        candidate = MagicMock()
        candidate.content = types.Content(
            role="model", parts=[types.Part(text=text)]
        )
        response.candidates = [candidate]
    elif function_calls:
        response.text = None
        response.function_calls = function_calls
        candidate = MagicMock()
        candidate.content = types.Content(
            role="model", parts=[types.Part(text="")]
        )
        response.candidates = [candidate]
    else:
        response.text = None
        response.function_calls = None
        response.candidates = []

    return response


class TestGenerateContent(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.working_dir = "./calculator"

    def test_text_response_returns_immediately(self):
        self.client.models.generate_content.return_value = make_mock_response(
            text="The bug is on line 5."
        )
        messages = []
        result = generate_content(self.client, messages, self.working_dir, verbose=False, tools_used=[])
        self.assertEqual(result, "The bug is on line 5.")
        self.assertEqual(self.client.models.generate_content.call_count, 1)

    def test_function_call_dispatches_and_returns_none(self):
        func_call = types.FunctionCall(
            name="get_files_info", args={"directory": "."}
        )
        self.client.models.generate_content.return_value = make_mock_response(
            function_calls=[func_call]
        )
        messages = []
        result = generate_content(self.client, messages, self.working_dir, verbose=False, tools_used=[])
        self.assertIsNone(result)

    def test_function_call_appends_tool_result_to_messages(self):
        func_call = types.FunctionCall(
            name="get_files_info", args={"directory": "."}
        )
        self.client.models.generate_content.return_value = make_mock_response(
            function_calls=[func_call]
        )
        messages = []
        generate_content(self.client, messages, self.working_dir, verbose=False, tools_used=[])
        last_message = messages[-1]
        self.assertEqual(last_message.role, "user")
        self.assertIsNotNone(last_message.parts[0].function_response)

    def test_unknown_function_returns_error_in_response(self):
        func_call = types.FunctionCall(
            name="nonexistent_tool", args={}
        )
        self.client.models.generate_content.return_value = make_mock_response(
            function_calls=[func_call]
        )
        messages = []
        generate_content(self.client, messages, self.working_dir, verbose=False, tools_used=[])
        last_message = messages[-1]
        func_response = last_message.parts[0].function_response
        self.assertIn("error", func_response.response)

    def test_missing_usage_metadata_raises(self):
        response = MagicMock()
        response.usage_metadata = None
        self.client.models.generate_content.return_value = response
        messages = []
        with self.assertRaises(RuntimeError):
            generate_content(self.client, messages, self.working_dir, verbose=False, tools_used=[])

    def test_multiple_function_calls_in_single_response(self):
        func_calls = [
            types.FunctionCall(name="get_files_info", args={"directory": "."}),
            types.FunctionCall(name="get_file_content", args={"file_path": "main.py"}),
        ]
        self.client.models.generate_content.return_value = make_mock_response(
            function_calls=func_calls
        )
        messages = []
        generate_content(self.client, messages, self.working_dir, verbose=False, tools_used=[])
        last_message = messages[-1]
        self.assertEqual(len(last_message.parts), 2)
        self.assertEqual(last_message.parts[0].function_response.name, "get_files_info")
        self.assertEqual(last_message.parts[1].function_response.name, "get_file_content")


class TestAgentLoop(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.working_dir = "./calculator"

    def test_loop_terminates_on_text_response(self):
        self.client.models.generate_content.side_effect = [
            make_mock_response(function_calls=[
                types.FunctionCall(name="get_files_info", args={"directory": "."})
            ]),
            make_mock_response(function_calls=[
                types.FunctionCall(name="get_file_content", args={"file_path": "main.py"})
            ]),
            make_mock_response(text="Found the bug: missing return statement."),
        ]
        messages = []
        final = None
        for _ in range(15):
            result = generate_content(self.client, messages, self.working_dir, verbose=False, tools_used=[])
            if result:
                final = result
                break

        self.assertEqual(final, "Found the bug: missing return statement.")
        self.assertEqual(self.client.models.generate_content.call_count, 3)

    def test_loop_hits_max_iterations(self):
        self.client.models.generate_content.return_value = make_mock_response(
            function_calls=[
                types.FunctionCall(name="get_files_info", args={"directory": "."})
            ]
        )
        messages = []
        max_iters = 5
        final = None
        for _ in range(max_iters):
            result = generate_content(self.client, messages, self.working_dir, verbose=False, tools_used=[])
            if result:
                final = result
                break

        self.assertIsNone(final)
        self.assertEqual(self.client.models.generate_content.call_count, max_iters)


if __name__ == "__main__":
    unittest.main()
