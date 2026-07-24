# AI Code Agent

A command-line coding agent that uses Google's Gemini API to autonomously debug and fix Python projects. Give it a prompt and point it at a directory — it explores the code, identifies issues, makes targeted fixes, and verifies they work, all through an iterative tool-use loop.

## How It Works

The agent runs a [ReAct-style](https://arxiv.org/abs/2210.03629) loop: on each iteration, Gemini either responds with a final answer or requests one or more tool calls. Tool results are fed back into the conversation, and the loop continues until the model produces a text response or hits the iteration limit.

```
User prompt
    │
    ▼
┌─────────────────────┐
│  Send messages to    │
│  Gemini with tools   │◄──────────────────┐
└─────────┬───────────┘                    │
          │                                │
          ▼                                │
    ┌───────────┐     YES    ┌───────────┐ │
    │ Function  │───────────►│ Execute   │ │
    │ calls?    │            │ tools     │─┘
    └─────┬─────┘            └───────────┘
          │ NO                (results appended
          ▼                   to messages)
    ┌───────────┐
    │ Print     │
    │ response  │
    └───────────┘
```

All tool calls are sandboxed to the specified working directory — the agent cannot read, write, or execute files outside of it.

## Setup

**Requirements:** Python 3.13+, a [Gemini API key](https://aistudio.google.com/apikey)

```bash
# Clone and install
git clone https://github.com/ervinjohn50/AI_agent.git
cd AI_agent
python -m venv .venv
source .venv/bin/activate
pip install -r pyproject.toml
```

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_api_key_here
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

## Usage

```bash
python main.py "your prompt here" --dir /path/to/project
```

**Flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--dir` | `.` (current directory) | Working directory the agent operates in |
| `--verbose` | off | Show token counts, function args, and tool results |

**Examples:**

```bash
# Debug a project in a specific directory
python main.py "the tests are failing, find and fix the bug" --dir ./my-project

# Explore a codebase
python main.py "explain the architecture of this project" --dir ~/repos/some-app

# Verbose mode to see the agent's tool calls
python main.py "find and fix the TypeError in main.py" --dir ./buggy-code --verbose
```

## Tools

The agent has access to five tools. Each tool enforces a directory boundary — it cannot operate outside the specified working directory.

| Tool | Description |
|------|-------------|
| `get_files_info` | Lists files and directories with sizes |
| `get_file_content` | Reads file contents (up to 10,000 characters) |
| `write_file` | Creates or overwrites a file |
| `run_python_file` | Executes a Python file and captures stdout/stderr (30s timeout) |
| `search_files` | Case-insensitive text search across all files, returns matching lines |

### Adding a New Tool

Each tool is a Python module in `functions/` with two exports: the function and its Gemini schema. To add one:

1. Create `functions/your_tool.py` with:
   - A function that takes `working_directory: str` as its first parameter
   - A `types.FunctionDeclaration` schema describing the tool for Gemini

2. Register it in `call_function.py`:
   - Import the function and schema
   - Add the schema to `available_functions`
   - Add the function to `function_map`

## Project Structure

```
├── main.py              # CLI entry point and agent loop
├── call_function.py     # Tool registry and dispatch
├── prompts.py           # System prompt for the agent
├── config.py            # Configuration constants
├── functions/
│   ├── get_files_info.py
│   ├── get_file_content.py
│   ├── write_file.py
│   ├── run_python_file.py
│   └── search_files.py
└── calculator/          # Sample project for testing the agent
```

## Configuration

Constants in `config.py`:

| Constant | Value | Purpose |
|----------|-------|---------|
| `MAX_ITERS` | 15 | Maximum agent loop iterations before stopping |
| `MAX_FILE_CHARS` | 10,000 | Truncation limit when reading file contents |
