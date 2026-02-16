"""Search tools for finding files and content."""

import os
import re
import glob as glob_module
from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel, Field
from jagent.core.tool import Tool


class GlobInput(BaseModel):
    """Input schema for Glob tool."""

    pattern: str = Field(
        description="Glob pattern to match files (e.g., '**/*.py', 'src/**/*.ts')"
    )
    path: Optional[str] = Field(
        default=None,
        description="Directory to search in (default: current directory)"
    )


class Glob(Tool):
    """
    Find files by pattern matching.

    Uses glob patterns to find files:
    - `*.py` - Python files in current dir
    - `**/*.py` - Python files recursively
    - `src/**/*.ts` - TypeScript files in src/
    """

    name = "glob"
    description = "Find files matching a glob pattern. Supports recursive patterns like **/*.py"
    input_schema = GlobInput

    def execute(
        self,
        pattern: str,
        path: Optional[str] = None,
    ) -> str:
        """
        Find files matching a pattern.

        Args:
            pattern: Glob pattern
            path: Directory to search in

        Returns:
            List of matching files
        """
        try:
            # Use current directory if no path provided
            search_path = path or os.getcwd()

            # Change to search directory
            original_dir = os.getcwd()
            try:
                os.chdir(search_path)

                # Find matching files
                matches = glob_module.glob(pattern, recursive=True)

                # Sort by modification time (most recent first)
                matches.sort(key=lambda x: os.path.getmtime(x) if os.path.exists(x) else 0, reverse=True)

                if not matches:
                    return f"No files found matching pattern: {pattern}"

                # Format output
                output_lines = [f"Found {len(matches)} file(s) matching '{pattern}':"]
                for match in matches[:100]:  # Limit to first 100
                    output_lines.append(f"  {match}")

                if len(matches) > 100:
                    output_lines.append(f"  ... and {len(matches) - 100} more")

                return '\n'.join(output_lines)

            finally:
                os.chdir(original_dir)

        except Exception as e:
            return f"Error finding files: {type(e).__name__}: {str(e)}"


class GrepInput(BaseModel):
    """Input schema for Grep tool."""

    pattern: str = Field(
        description="Regular expression pattern to search for"
    )
    path: Optional[str] = Field(
        default=None,
        description="File or directory to search in (default: current directory)"
    )
    file_pattern: Optional[str] = Field(
        default="*",
        description="File pattern to filter (e.g., '*.py', '*.{ts,tsx}')"
    )
    case_insensitive: bool = Field(
        default=False,
        description="Case-insensitive search"
    )
    max_results: int = Field(
        default=50,
        description="Maximum number of results to return"
    )


class Grep(Tool):
    """
    Search file contents using regular expressions.

    Similar to grep/ripgrep - searches for patterns in files.
    Returns matching lines with file paths and line numbers.
    """

    name = "grep"
    description = "Search file contents using regex. Returns matching lines with file and line numbers."
    input_schema = GrepInput

    def execute(
        self,
        pattern: str,
        path: Optional[str] = None,
        file_pattern: Optional[str] = "*",
        case_insensitive: bool = False,
        max_results: int = 50,
    ) -> str:
        """
        Search for pattern in files.

        Args:
            pattern: Regex pattern to search for
            path: Path to search in
            file_pattern: File pattern filter
            case_insensitive: Case-insensitive search
            max_results: Maximum results

        Returns:
            Matching lines with locations
        """
        try:
            # Compile regex
            flags = re.IGNORECASE if case_insensitive else 0
            regex = re.compile(pattern, flags)

            # Get search path
            search_path = path or os.getcwd()

            # Find files to search
            if os.path.isfile(search_path):
                files = [search_path]
            else:
                # Find files matching pattern
                files = []
                for root, dirs, filenames in os.walk(search_path):
                    # Skip hidden directories
                    dirs[:] = [d for d in dirs if not d.startswith('.')]

                    for filename in filenames:
                        if self._matches_file_pattern(filename, file_pattern or "*"):
                            files.append(os.path.join(root, filename))

            # Search in files
            results = []
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            if regex.search(line):
                                # Make path relative if possible
                                try:
                                    rel_path = os.path.relpath(file_path)
                                except ValueError:
                                    rel_path = file_path

                                results.append({
                                    'file': rel_path,
                                    'line': line_num,
                                    'content': line.rstrip(),
                                })

                                if len(results) >= max_results:
                                    break

                    if len(results) >= max_results:
                        break

                except (PermissionError, IsADirectoryError):
                    # Skip files we can't read
                    continue

            if not results:
                return f"No matches found for pattern: {pattern}"

            # Format output
            output_lines = [f"Found {len(results)} match(es) for '{pattern}':"]
            for result in results:
                output_lines.append(
                    f"  {result['file']}:{result['line']}: {result['content']}"
                )

            if len(results) >= max_results:
                output_lines.append(f"  ... (limited to {max_results} results)")

            return '\n'.join(output_lines)

        except re.error as e:
            return f"Error: Invalid regex pattern: {str(e)}"

        except Exception as e:
            return f"Error searching files: {type(e).__name__}: {str(e)}"

    def _matches_file_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches the file pattern."""
        # Handle patterns like *.{ts,tsx}
        if '{' in pattern and '}' in pattern:
            # Convert to regex
            pattern = pattern.replace('.', r'\.')
            pattern = pattern.replace('*', '.*')
            pattern = pattern.replace('{', '(')
            pattern = pattern.replace('}', ')')
            pattern = pattern.replace(',', '|')
            return bool(re.match(pattern + '$', filename))
        else:
            # Simple glob matching
            return glob_module.fnmatch.fnmatch(filename, pattern)
