# test_run_python_file.py
from functions.run_python_file import run_python_file

if __name__ == "__main__":
    print("Running main.py:")
    print(run_python_file("calculator", "main.py"))
    print("")

    print("Running main.py with args:")
    print(run_python_file("calculator", "main.py", ["3 + 5"]))
    print("")

    print("Running tests.py:")
    print(run_python_file("calculator", "tests.py"))
    print("")

    print("Running ../main.py (should error):")
    print(run_python_file("calculator", "../main.py"))
    print("")

    print("Running nonexistent.py (should error):")
    print(run_python_file("calculator", "nonexistent.py"))
    print("")

    print("Running lorem.txt (should error):")
    print(run_python_file("calculator", "lorem.txt"))