import logging
import re
import os
from typing import Dict, Any, List, Tuple

from src.core.interfaces import PipelineTask
from src.core.context import WorkflowContext
from src.core.registry import register_task

logger = logging.getLogger(__name__)


@register_task("TextFileSplitterTask")
class TextFileSplitterTask(PipelineTask):
    """
    Reads a single large text file, splits it by a delimiter (e.g., '%%% filename'),
    and populates the context with a list of documents.
    """

    # Regex to match "%%% filename"
    DELIMITER_PATTERN = re.compile(r"^%%%\s+(.+)$")

    def execute(
        self, context: WorkflowContext, config: Dict[str, Any]
    ) -> WorkflowContext:
        input_file = config.get("input_file")
        output_key = config.get("output_key", "split_docs")
        save_to_disk = config.get("save_to_disk", False)
        output_dir = config.get("output_dir", "./outputs/split_files")

        if not input_file or not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")

        logger.info(f"Splitting file: {input_file}")

        with open(input_file, encoding="utf-8") as f:
            content = f.read()

        sections = self._parse_content(content)

        if not sections:
            logger.warning(
                "No sections found using '%%%' delimiter. treating file as single doc."
            )
            base_name = os.path.basename(input_file)
            sections = [(base_name, content)]

        # Convert to standard document format for the pipeline
        # Structure: [{'filename': '...', 'content': '...'}]
        doc_list = []
        for filename, text in sections:
            # Ensure .txt extension for consistency
            if not filename.endswith(".txt"):
                safe_filename = f"{self._sanitize_filename(filename)}.txt"
            else:
                safe_filename = self._sanitize_filename(filename)

            doc_list.append(
                {
                    "filename": safe_filename,
                    "content": text,
                    "filepath": f"virtual/{safe_filename}",  # Virtual path since it exists in memory
                }
            )

            # Optional: Write to disk (mimicking your original script)
            if save_to_disk:
                self._save_file(output_dir, safe_filename, text)

        # Store in context
        context.set(output_key, doc_list)
        logger.info(
            f"Splitter produced {len(doc_list)} documents into key '{output_key}'."
        )

        return context

    def _parse_content(self, content: str) -> List[Tuple[str, str]]:
        lines = content.splitlines()
        sections: List[Tuple[str, str]] = []

        current_filename = None
        current_buffer = []

        for line in lines:
            match = self.DELIMITER_PATTERN.match(line)
            if match:
                # Close previous section
                if current_filename:
                    sections.append(
                        (current_filename, "\n".join(current_buffer).strip())
                    )

                # Start new section
                current_filename = match.group(1).strip()
                current_buffer = []
            else:
                if current_filename is not None:
                    current_buffer.append(line)

        # Append final section
        if current_filename and current_buffer:
            sections.append((current_filename, "\n".join(current_buffer).strip()))

        return sections

    def _sanitize_filename(self, name: str) -> str:
        return "".join(c for c in name if c.isalnum() or c in ("_", "-", " "))

    def _save_file(self, folder: str, filename: str, content: str):
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.debug(f"Saved split file: {path}")
