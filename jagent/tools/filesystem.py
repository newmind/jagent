"""Filesystem tools for reading, writing, and editing files."""

import os
from typing import Optional
from pydantic import BaseModel, Field
from jagent.core.tool import Tool


class FileReadInput(BaseModel):
    """Input schema for FileRead tool."""

    file_path: str = Field(
        description="Absolute path to the file to read"
    )
    offset: Optional[int] = Field(
        default=None,
        description="Line number to start reading from (1-indexed)"
    )
    limit: Optional[int] = Field(
        default=None,
        description="Number of lines to read"
    )


class FileRead(Tool):
    """
    Read files from the filesystem.

    Supports reading entire files or specific line ranges.
    Returns file contents with line numbers (like cat -n).
    """

    name = "file_read"
    description = "Read a file from the filesystem. Returns file contents with line numbers."
    input_schema = FileReadInput

    def execute(
        self,
        file_path: str,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        """
        Read a file and return its contents.

        Args:
            file_path: Path to the file
            offset: Starting line number (1-indexed)
            limit: Number of lines to read

        Returns:
            File contents with line numbers
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return f"Error: File not found: {file_path}"

            if not os.path.isfile(file_path):
                return f"Error: Not a file: {file_path}"

            # Read the file
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()

            # Apply offset and limit
            start = (offset - 1) if offset else 0
            end = (start + limit) if limit else len(lines)

            lines = lines[start:end]

            # Format with line numbers (Claude Code style)
            formatted_lines = []
            for i, line in enumerate(lines, start=start + 1):
                # Remove trailing newline for formatting
                line = line.rstrip('\n')
                formatted_lines.append(f"{i:6d}→{line}")

            return '\n'.join(formatted_lines)

        except Exception as e:
            return f"Error reading file: {type(e).__name__}: {str(e)}"


class FileWriteInput(BaseModel):
    """Input schema for FileWrite tool."""

    file_path: str = Field(
        description="Absolute path to the file to write"
    )
    content: str = Field(
        description="Content to write to the file"
    )


class FileWrite(Tool):
    """
    Write content to a file.

    Creates a new file or overwrites an existing file.
    Creates parent directories if they don't exist.
    """

    name = "file_write"
    description = "Write content to a file. Creates new file or overwrites existing."
    input_schema = FileWriteInput

    def execute(self, file_path: str, content: str) -> str:
        """
        Write content to a file.

        Args:
            file_path: Path to the file
            content: Content to write

        Returns:
            Success message or error
        """
        try:
            # Create parent directories if needed
            parent_dir = os.path.dirname(file_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir)

            # Write the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # Get file size
            size = os.path.getsize(file_path)
            lines = content.count('\n') + 1

            return f"Successfully wrote {lines} lines ({size} bytes) to {file_path}"

        except Exception as e:
            return f"Error writing file: {type(e).__name__}: {str(e)}"


class FileEditInput(BaseModel):
    """Input schema for FileEdit tool."""

    file_path: str = Field(
        description="Absolute path to the file to edit"
    )
    old_string: str = Field(
        description="Text to find and replace"
    )
    new_string: str = Field(
        description="Text to replace it with"
    )
    replace_all: bool = Field(
        default=False,
        description="Replace all occurrences (default: False, replaces first only)"
    )


class FileEdit(Tool):
    """
    Edit files using find-and-replace.

    Finds exact string matches and replaces them.
    Can replace first occurrence or all occurrences.
    """

    name = "file_edit"
    description = "Edit a file by replacing text. Finds exact matches and replaces them."
    input_schema = FileEditInput

    def execute(
        self,
        file_path: str,
        old_string: str,
        new_string: str,
        replace_all: bool = False,
    ) -> str:
        """
        Edit a file using find-and-replace.

        Args:
            file_path: Path to the file
            old_string: Text to find
            new_string: Text to replace with
            replace_all: Whether to replace all occurrences

        Returns:
            Success message or error
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return f"Error: File not found: {file_path}"

            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check if old_string exists
            if old_string not in content:
                return f"Error: String not found in file: {old_string[:50]}..."

            # Replace
            if replace_all:
                count = content.count(old_string)
                new_content = content.replace(old_string, new_string)
                message = f"Replaced {count} occurrence(s)"
            else:
                new_content = content.replace(old_string, new_string, 1)
                message = "Replaced 1 occurrence"

            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            return f"Successfully edited {file_path}: {message}"

        except Exception as e:
            return f"Error editing file: {type(e).__name__}: {str(e)}"
