# Project Name
...

## Features
...

## Setup

This project uses `uv` for dependency management. To set up the project, follow
these steps:

1. **Install uv**: If you don't have `uv` installed, you can install it using
   pip:
   - if you're on windows:
   ```sh
   winget install --id=astral-sh.uv -e
   ```

   - if you're on linux:
   ```sh
   # use your system's package manager
   apt install uv # debian based distros
   dnf install uv # RHEL/Fedora based distros
   pacman -S uv # Archlinux
   ```

   - if you're on macOS:
   ```sh
   # use homebrew
   brew install uv
   ```
2. **Create a virtual environment and install dependencies**: Navigate to the
   project directory and run:

   ```bash
   uv venv
   uv sync
   ```

3. **Activate the virtual environment**:
   - On Linux/macOS:
     ```bash
     source .venv/bin/activate
     ```
   - On Windows:
     ```sh
     .venv\Scripts\activate
     ```

## Coding Rules

- Make use of the gradual typing system in python. It helps tools to give us better diagnostics & intellisense/autocompletion.
- use ruff for formatting code & diagnostics [install the vscode extension](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff).
- use [pylance vscode extension](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance) for intellisense/autocompletion.

### Python Typing Examples

To ensure type safety and improve code readability, please use Python's typing
system. Here are some basic examples:

```py
from typing import List, Dict, Optional

def greet(name: str) -> str:
    return f"Hello, {name}"

def add_numbers(a: int, b: int) -> int:
    return a + b

def get_items(items: List[str]) -> None:
    for item in items:
        print(item)

def find_user(user_id: int) -> Optional[Dict[str, str]]:
    users = {1: {"name": "Alice"}, 2: {"name": "Bob"}}
    return users.get(user_id)

class MyClass:
    def __init__(self, value: int):
        self.value: int = value

    def get_value(self) -> int:
        return self.value
```
