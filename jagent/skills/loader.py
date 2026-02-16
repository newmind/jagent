"""Plugin/skill loader for dynamically loading custom tools."""

import importlib
import importlib.util
import sys
from pathlib import Path
from typing import List, Optional, Type
from jagent.core.tool import Tool


class SkillLoader:
    """
    Load custom tools/skills from Python files or modules.

    Skills are Python files that export Tool subclasses.
    This allows users to extend the agent with custom functionality.

    Example skill file (my_skill.py):
        from jagent import Tool
        from pydantic import BaseModel

        class MyToolInput(BaseModel):
            data: str

        class MyTool(Tool):
            name = "my_tool"
            description = "My custom tool"
            input_schema = MyToolInput

            def execute(self, data: str) -> str:
                return f"Processed: {data}"

    Usage:
        loader = SkillLoader()
        tools = loader.load_from_file("my_skill.py")
        agent.add_tools(tools)
    """

    def __init__(self) -> None:
        """Initialize the skill loader."""
        self._loaded_modules = []

    def load_from_file(self, file_path: str) -> List[Tool]:
        """
        Load tools from a Python file.

        Args:
            file_path: Path to Python file containing Tool subclasses

        Returns:
            List of Tool instances found in the file
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Skill file not found: {file_path}")

        # Load the module
        module_name = f"jagent_skill_{path.stem}"
        spec = importlib.util.spec_from_file_location(module_name, path)

        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load module from {file_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        self._loaded_modules.append(module)

        # Find all Tool subclasses in the module
        tools = self._extract_tools_from_module(module)

        return tools

    def load_from_module(self, module_name: str) -> List[Tool]:
        """
        Load tools from an installed Python module.

        Args:
            module_name: Name of the module to import

        Returns:
            List of Tool instances found in the module
        """
        module = importlib.import_module(module_name)
        self._loaded_modules.append(module)

        tools = self._extract_tools_from_module(module)

        return tools

    def load_from_directory(self, directory_path: str) -> List[Tool]:
        """
        Load all tools from Python files in a directory.

        Args:
            directory_path: Path to directory containing skill files

        Returns:
            List of all Tool instances found
        """
        path = Path(directory_path)

        if not path.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory_path}")

        tools = []

        # Load all .py files in the directory
        for file_path in path.glob("*.py"):
            if file_path.name.startswith("_"):
                # Skip private files
                continue

            try:
                file_tools = self.load_from_file(str(file_path))
                tools.extend(file_tools)
            except Exception as e:
                print(f"Warning: Failed to load {file_path}: {e}")

        return tools

    def _extract_tools_from_module(self, module) -> List[Tool]:
        """
        Extract Tool subclasses from a module.

        Args:
            module: Python module object

        Returns:
            List of Tool instances
        """
        tools = []

        for name in dir(module):
            obj = getattr(module, name)

            # Check if it's a class
            if not isinstance(obj, type):
                continue

            # Check if it's a Tool subclass (but not Tool itself)
            if issubclass(obj, Tool) and obj is not Tool:
                try:
                    # Try to instantiate
                    tool = obj()
                    tools.append(tool)
                except Exception as e:
                    print(f"Warning: Failed to instantiate {name}: {e}")

        return tools

    def __repr__(self) -> str:
        return f"<SkillLoader: {len(self._loaded_modules)} modules loaded>"
