import logging
import os
from typing import Dict, Any

from src.core.interfaces import PipelineTask
from src.core.context import WorkflowContext
from src.core.registry import register_task

logger = logging.getLogger(__name__)


@register_task("ReportWriterTask")
class ReportWriterTask(PipelineTask):
    """
    Compiles a final Markdown report from multiple context variables.
    Config 'sections' is a list of dicts: {'title': '...', 'content_key': '...'}
    """

    def execute(
        self, context: WorkflowContext, config: Dict[str, Any]
    ) -> WorkflowContext:
        filename = config.get("filename")
        sections = config.get("sections", [])

        if not filename:
            raise ValueError("ReportWriterTask requires a 'filename'.")

        report_content = []

        for section in sections:
            title = section.get("title")
            key = section.get("content_key")

            content = context.get(key, f"_[Missing content for key: {key}]_")

            if title:
                report_content.append(f"## {title}")

            report_content.append(str(content))
            report_content.append("\n---\n")

        # Write to disk
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n\n".join(report_content))

        logger.info(f"Final Report saved to {filename}")
        return context
