"""
CODEBASE CONTEXT GENERATOR
--------------------------
Purpose:
    This script scans a specified directory, filters for relevant code files,
    and consolidates them into a single Markdown (.md) document.

    The output serves as a comprehensive context dump for Large Language Models
    (LLMs) like Gemini, Claude, or GitHub Copilot, enabling them to understand
    the full project structure and logic.

Key Features:
    1. **Visual Hierarchy:** Generates a text-based directory tree.
    2. **Content Aggregation:** Wraps file contents in correct code blocks.
    3. **High Reliability:** Implements "Fail Fast" validations and robust error
       handling for encoding or permission issues.
    4. **Modular Design:** Refactored into a reusable `CodebaseContextGenerator`
       class, separating CLI logic from core functionality.

How to Run:
    # Standard usage
    python generate_context.py ./src

    # Custom output location
    python generate_context.py ./src --output my_context.md

Requirements:
    - Python 3.10+ (Uses dataclasses, pathlib, and modern type hinting).
    - Standard Library only (No `pip install` required).
"""

import os
import argparse
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Set, Iterator, Tuple, List

# --- Configuration & Constants ---

# Default settings (sensible defaults)
DEFAULT_IGNORE_DIRS = {
    "__pycache__",
    ".git",
    ".idea",
    ".vscode",
    "venv",
    "env",
    "node_modules",
    "dist",
    "build",
    "migrations",
    "coverage",
}

DEFAULT_INCLUDE_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".html",
    ".css",
    ".md",
    ".json",
    ".yaml",
    ".yml",
    ".sql",
    ".toml",
    ".txt",
    ".java",
    ".c",
    ".cpp",
}

# Setup Logging (Signal errors explicitly)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GeneratorConfig:
    """
    Immutable configuration object.
    Prevents magic values and brittle assumptions in the main logic.
    """

    target_dir: Path
    output_file: Path
    ignore_dirs: Set[str] = field(default_factory=lambda: DEFAULT_IGNORE_DIRS)
    include_extensions: Set[str] = field(
        default_factory=lambda: DEFAULT_INCLUDE_EXTENSIONS
    )

    def __post_init__(self):
        # Fail fast if target does not exist
        if not self.target_dir.exists() or not self.target_dir.is_dir():
            raise FileNotFoundError(f"Target directory not found: {self.target_dir}")


class CodebaseContextGenerator:
    """
    Handles the logic of scanning, filtering, and formatting codebase context.
    Encapsulates related data and behavior.
    """

    def __init__(self, config: GeneratorConfig):
        self.config = config

    def generate(self) -> None:
        """
        Orchestrates the context generation process.
        """
        logger.info(f"Scanning: {self.config.target_dir}")

        try:
            tree_content = self._generate_tree_structure()
            file_contents = list(self._collect_file_contents())

            self._write_output(tree_content, file_contents)

            logger.info(f"Success! Context written to '{self.config.output_file}'")
            self._log_stats(file_contents)

        except PermissionError as e:
            logger.error(f"Permission denied: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")

    def _generate_tree_structure(self) -> str:
        """
        Generates a visual directory tree string.
        """
        tree_lines: List[str] = [f"Directory Tree for: {self.config.target_dir.name}/"]

        # Use os.walk for efficient directory traversal
        for root, dirs, files in os.walk(self.config.target_dir):
            # Mutate dirs in-place to prevent walking ignored directories
            dirs[:] = [d for d in dirs if d not in self.config.ignore_dirs]

            current_path = Path(root)
            level = str(current_path.relative_to(self.config.target_dir.parent)).count(
                os.sep
            )

            if current_path != self.config.target_dir:
                indent = "    " * (level - 1)
                tree_lines.append(f"{indent}{current_path.name}/")

            sub_indent = "    " * level
            for file in sorted(files):
                if Path(file).suffix in self.config.include_extensions:
                    tree_lines.append(f"{sub_indent}{file}")

        return "\n".join(tree_lines)

    def _collect_file_contents(self) -> Iterator[Tuple[Path, str]]:
        """
        Generator that yields (relative_path, content).
        Lazy evaluation ensures memory efficiency for large projects.
        """
        for root, dirs, files in os.walk(self.config.target_dir):
            dirs[:] = [d for d in dirs if d not in self.config.ignore_dirs]

            for file_name in sorted(files):
                file_path = Path(root) / file_name

                if file_path.suffix not in self.config.include_extensions:
                    continue

                try:
                    # Explicit encoding handling
                    content = file_path.read_text(encoding="utf-8")
                    rel_path = file_path.relative_to(self.config.target_dir.parent)
                    yield rel_path, content
                except UnicodeDecodeError:
                    logger.warning(
                        f"Skipping binary or non-utf8 file: {file_path.name}"
                    )
                except Exception as e:
                    logger.warning(f"Could not read {file_path.name}: {e}")

    def _write_output(self, tree: str, files: List[Tuple[Path, str]]) -> None:
        """
        Writes the formatted data to the output file.
        """
        with open(self.config.output_file, "w", encoding="utf-8") as f:
            # Header
            f.write(f"# Codebase Context: {self.config.target_dir.name}\n\n")

            # Section 1: Tree
            f.write("## 1. Directory Structure\n")
            f.write("```text\n")
            f.write(tree)
            f.write("\n```\n\n")

            f.write("---\n\n## 2. File Contents\n\n")

            # Section 2: Files
            for rel_path, content in files:
                ext = rel_path.suffix.lstrip(".")
                f.write(f"### `{rel_path}`\n\n")
                f.write(f"```{ext}\n")
                f.write(content)
                f.write("\n```\n\n")

    def _log_stats(self, files: List[Tuple[Path, str]]) -> None:
        """
        Calculates and logs file count and estimated token usage.
        """
        total_chars = 0
        if self.config.output_file.exists():
            total_chars = self.config.output_file.stat().st_size

        est_tokens = total_chars // 4
        logger.info("-" * 30)
        logger.info(f"Files Processed:    {len(files)}")
        logger.info(f"Total Context Size: {total_chars:,} chars")
        logger.info(f"Estimated Tokens:   ~{est_tokens:,}")
        logger.info("-" * 30)


# --- CLI Entry Point ---


def main():
    parser = argparse.ArgumentParser(
        description="Consolidate code files into a single Markdown file for LLM context."
    )
    parser.add_argument("target_dir", help="The directory to scan (e.g., ./src)")
    parser.add_argument(
        "--output",
        "-o",
        default="codebase_context.md",
        help="Output file name (default: codebase_context.md)",
    )

    args = parser.parse_args()

    try:
        config = GeneratorConfig(
            target_dir=Path(args.target_dir).resolve(),
            output_file=Path(args.output).resolve(),
        )

        generator = CodebaseContextGenerator(config)
        generator.generate()

    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        exit(1)


if __name__ == "__main__":
    main()
