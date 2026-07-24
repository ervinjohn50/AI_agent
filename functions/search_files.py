import os
from google.genai import types


def search_files(working_directory: str, pattern: str, directory: str = ".") -> str:
    try:
        abs_working_dir = os.path.abspath(working_directory)
        target_dir = os.path.normpath(os.path.join(abs_working_dir, directory))

        if os.path.commonpath([abs_working_dir, target_dir]) != abs_working_dir:
            return f'Error: Cannot search "{directory}" as it is outside the permitted working directory'

        if not os.path.isdir(target_dir):
            return f'Error: "{directory}" is not a directory'

        matches = []
        for root, _, files in os.walk(target_dir):
            for filename in files:
                file_path = os.path.join(root, filename)
                rel_path = os.path.relpath(file_path, abs_working_dir)
                try:
                    with open(file_path, "r") as f:
                        for line_num, line in enumerate(f, 1):
                            if pattern.lower() in line.lower():
                                matches.append(f"{rel_path}:{line_num}: {line.rstrip()}")
                except (UnicodeDecodeError, PermissionError):
                    continue

        if not matches:
            return f'No matches found for "{pattern}"'

        return "\n".join(matches)

    except Exception as e:
        return f"Error: {e}"


schema_search_files = types.FunctionDeclaration(
    name="search_files",
    description="Searches for a text pattern across all files in a directory. Returns matching filenames, line numbers, and line content. The search is case-insensitive.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "pattern": types.Schema(
                type=types.Type.STRING,
                description="Text pattern to search for across files",
            ),
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Directory to search in, relative to the working directory (default is the working directory itself)",
            ),
        },
        required=["pattern"],
    ),
)
