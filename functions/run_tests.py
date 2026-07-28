import os
import subprocess
import sys
from google.genai import types


def run_tests(working_directory: str, test_file: str | None = None) -> str:
    try:
        abs_working_dir = os.path.abspath(working_directory)

        if not os.path.isdir(abs_working_dir):
            return f'Error: "{working_directory}" is not a valid directory'

        if test_file:
            abs_test_path = os.path.normpath(
                os.path.join(abs_working_dir, test_file)
            )
            if os.path.commonpath([abs_working_dir, abs_test_path]) != abs_working_dir:
                return f'Error: Cannot run "{test_file}" as it is outside the permitted working directory'
            if not os.path.isfile(abs_test_path):
                return f'Error: "{test_file}" does not exist'

        framework = detect_framework(abs_working_dir)

        if framework == "pytest":
            command = [sys.executable, "-m", "pytest", "-v"]
            if test_file:
                command.append(test_file)
        else:
            command = [sys.executable, "-m", "unittest"]
            if test_file:
                command.append(test_file)
            else:
                command.extend(["discover", "-v"])

        result = subprocess.run(
            command,
            cwd=abs_working_dir,
            capture_output=True,
            text=True,
            timeout=60,
        )

        output = ""
        if result.returncode == 0:
            output += "Tests PASSED\n"
        else:
            output += "Tests FAILED\n"

        if result.stdout:
            output += f"STDOUT:\n{result.stdout}"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}"

        return output

    except subprocess.TimeoutExpired:
        return "Error: tests timed out after 60 seconds"
    except Exception as e:
        return f"Error: {e}"


def detect_framework(directory: str) -> str:
    pytest_indicators = ["pytest.ini", "conftest.py", "setup.cfg"]
    for indicator in pytest_indicators:
        if os.path.isfile(os.path.join(directory, indicator)):
            return "pytest"

    pyproject_path = os.path.join(directory, "pyproject.toml")
    if os.path.isfile(pyproject_path):
        with open(pyproject_path, "r") as f:
            if "pytest" in f.read():
                return "pytest"

    check = subprocess.run(
        [sys.executable, "-m", "pytest", "--version"],
        capture_output=True,
        text=True,
    )
    if check.returncode == 0:
        return "pytest"

    return "unittest"


schema_run_tests = types.FunctionDeclaration(
    name="run_tests",
    description="Detects the testing framework (pytest or unittest) and runs the test suite in the working directory. Can optionally run a specific test file.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "test_file": types.Schema(
                type=types.Type.STRING,
                description="Optional path to a specific test file to run, relative to the working directory. If omitted, discovers and runs all tests.",
            ),
        },
    ),
)
