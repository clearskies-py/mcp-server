"""
Style guide resources for clearskies framework.

This module provides resource functions that return style guide documentation
for writing clearskies code.
"""

import textwrap


def style_docstrings() -> str:
    """Docstring style guide for clearskies framework code."""
    return textwrap.dedent("""\
        # clearskies Docstring Style Guide

        This guide describes the docstring conventions used in the clearskies framework.

        ## General Principles

        1. **Triple-quoted strings** – Always use `\"\"\"` for docstrings
        2. **Brief first line** – Start with a concise summary (one line when possible)
        3. **Markdown formatting** – Use markdown for emphasis, code blocks, lists
        4. **Complete examples** – Show full working code, not fragments
        5. **Demonstrate usage** – Include bash/curl commands showing real execution

        ## Class Docstrings

        Class docstrings should explain the purpose and philosophy of the class.

        ## Attribute/Property Docstrings

        Configuration attributes should have comprehensive docstrings that include:

        1. **Summary** – One-line description of what it does
        2. **Explanation** – Detailed description of behavior
        3. **Code example** – Complete working code demonstrating usage
        4. **Execution example** – Bash/curl commands showing real usage

        ## Key Formatting Rules

        1. **Indentation** – Use 4 spaces for docstring content indentation
        2. **Code blocks** – Always use ``` with language identifier (python, bash)
        3. **Spacing** – Add blank line between sections for readability
        4. **Shell prompts** – Use `$` for shell commands in bash blocks
        5. **Output** – Show actual output after shell commands
        6. **Imports** – Always include necessary imports in examples
        7. **Complete context** – Show endpoint + context together, not just fragments
        8. **Real data** – Use realistic example data (names, emails, etc.)
    """)
