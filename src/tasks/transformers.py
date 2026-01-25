import os
import logging
import datetime
from typing import Dict, Any

from src.core.interfaces import PipelineTask
from src.core.context import WorkflowContext
from src.core.registry import register_task
from src.core.llm import get_llm_client

logger = logging.getLogger(__name__)


@register_task("LLMTransformTask")
class LLMTransformTask(PipelineTask):
    """
    Applies an LLM prompt to a single string input.
    """

    def execute(
        self, context: WorkflowContext, config: Dict[str, Any]
    ) -> WorkflowContext:
        input_key = config.get("input_key")
        output_key = config.get("output_key")
        prompt_file = config.get("prompt_file")
        model_name = config.get("model", "default")

        if not input_key or not output_key or not prompt_file:
            raise ValueError("LLMTransformTask config missing required keys.")

        # Load Data
        input_text = context.require(input_key)

        # Load Prompt
        if not os.path.exists(prompt_file):
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
        with open(prompt_file, encoding="utf-8") as f:
            template = f.read()

        # Execute
        llm_client = get_llm_client(config)
        final_prompt = template.format(content=input_text)

        logger.info(f"Generating transformation for key '{input_key}'...")
        result = llm_client.query(final_prompt, model=model_name)

        # Add Metadata (No Source field for single transform)
        current_date = datetime.datetime.now().strftime("%d-%m-%Y")
        metadata_section = (
            f"## Metadata\n"
            f"- **Date:** {current_date}\n"
            f"- **Model:** {model_name}\n"
            f"- **Prompt:** {prompt_file}\n\n"
        )

        # Combine
        final_output = f"{metadata_section}## LLM Processed Content\n\n{result}"

        context.set(output_key, final_output)
        return context


@register_task("BatchLLMTask")
class BatchLLMTask(PipelineTask):
    """
    Iterates over a list of items in the Context, applies an LLM prompt,
    and optionally saves the result to disk immediately.
    """

    def execute(
        self, context: WorkflowContext, config: Dict[str, Any]
    ) -> WorkflowContext:
        # 1. Configuration Extraction
        input_key = config.get("input_key")  # Key containing list of file dicts
        output_key = config.get("output_key")  # Key to store results list
        prompt_file = config.get("prompt_file")  # Path to .txt template
        save_intermediate = config.get("save_intermediate_files", False)
        output_dir = config.get("output_dir", "./outputs")
        suffix = config.get("filename_suffix", "_processed")
        model_name = config.get("model", "default")
        include_original = config.get("include_original_content", True)

        # 2. Validation
        if not input_key or not output_key or not prompt_file:
            raise ValueError(
                "BatchLLMTask requires 'input_key', 'output_key', and 'prompt_file'."
            )

        # 3. Load Resources
        inputs = context.require(input_key)  # Expecting List[Dict] from DirectoryLoader

        # Read the prompt template
        if not os.path.exists(prompt_file):
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
        with open(prompt_file, encoding="utf-8") as f:
            prompt_template = f.read()

        # Initialize LLM
        llm_client = get_llm_client(config)
        results = []

        # 4. Processing Loop
        logger.info(f"BatchLLMTask starting processing for {len(inputs)} items...")

        os.makedirs(output_dir, exist_ok=True)

        current_date = datetime.datetime.now().strftime("%d-%m-%Y")

        for item in inputs:
            original_filename = item.get("filename", "unknown")
            content = item.get("content", "")

            logger.info(f"Processing item: {original_filename}")

            # A. Prepare Prompt
            # We assume the template uses {content} as the placeholder
            final_prompt = prompt_template.format(content=content)

            # B. Call LLM
            try:
                llm_output = llm_client.query(final_prompt, model=model_name)
            except Exception as e:
                logger.error(f"LLM failure for {original_filename}: {e}")
                llm_output = f"[Error processing {original_filename}]"

            # C. Combine for Output
            metadata_section = (
                f"## Metadata\n"
                f"- **Date:** {current_date}\n"
                f"- **Source:** {original_filename}\n"
                f"- **Model:** {model_name}\n"
                f"- **Prompt:** {prompt_file}\n\n"
            )

            if include_original:
                processed_content = f"{metadata_section}## LLM Processed Content\n\n{llm_output}\n\n---\n\n## Original Content\n\n{content}"
            else:
                processed_content = (
                    f"{metadata_section}## LLM Processed Content\n\n{llm_output}"
                )

            # D. Save Intermediate File (optional)
            if save_intermediate:
                base_name = os.path.splitext(original_filename)[0]
                out_filename = f"{base_name}{suffix}.md"
                out_path = os.path.join(output_dir, out_filename)

                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(processed_content)
                logger.info(f"Saved intermediate file: {out_path}")

            # E. Store result in memory
            results.append(processed_content)

        # 5. Update Context
        context.set(output_key, results)
        return context
