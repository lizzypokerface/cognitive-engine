import glob
import os
import logging
from typing import Dict, Any

from src.core.interfaces import PipelineTask
from src.core.context import WorkflowContext
from src.core.registry import register_task

logger = logging.getLogger(__name__)


@register_task("DirectoryLoader")
class DirectoryLoader(PipelineTask):
    """
    Loads raw text files from a directory into the Context.
    Output in Context: A list of dictionaries [{'filename': '...', 'content': '...'}, ...]
    """

    def execute(
        self, context: WorkflowContext, config: Dict[str, Any]
    ) -> WorkflowContext:
        input_pattern = config.get("input_path")  # e.g., "./inputs/*.txt"
        output_key = config.get("output_key", "raw_files")

        if not input_pattern:
            raise ValueError("DirectoryLoader requires 'input_path' in config.")

        files = glob.glob(input_pattern)
        logger.info(
            f"DirectoryLoader found {len(files)} files matching '{input_pattern}'"
        )

        loaded_data = []
        for filepath in files:
            try:
                with open(filepath, encoding="utf-8") as f:
                    content = f.read()

                filename = os.path.basename(filepath)
                loaded_data.append(
                    {"filename": filename, "filepath": filepath, "content": content}
                )
            except Exception as e:
                logger.error(f"Failed to read file {filepath}: {e}")

        # Store the list in the context
        context.set(output_key, loaded_data)
        logger.info(f"Loaded {len(loaded_data)} files into context key '{output_key}'.")

        return context
