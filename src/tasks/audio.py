import logging
import os
import glob
from typing import Dict, Any
import torch

# Import whisper inside the class or method to avoid loading it if not used
# import whisper

from src.core.interfaces import PipelineTask
from src.core.context import WorkflowContext
from src.core.registry import register_task

logger = logging.getLogger(__name__)


@register_task("AudioTranscribeTask")
class AudioTranscribeTask(PipelineTask):
    """
    Transcribes audio files using local OpenAI Whisper.
    Output in Context: A list of dictionaries [{'filename': '...', 'content': '...'}, ...]
    Compatible with BatchLLMTask input requirements.
    """

    def execute(
        self, context: WorkflowContext, config: Dict[str, Any]
    ) -> WorkflowContext:
        input_pattern = config.get("input_path")  # e.g., "./audio/*.mp3"
        output_key = config.get("output_key", "transcribed_docs")
        model_size = config.get("model_size", "base")
        save_to_disk = config.get("save_to_disk", False)
        output_dir = config.get("output_dir", "./outputs/transcripts")

        if not input_pattern:
            raise ValueError("AudioTranscribeTask requires 'input_path'.")

        # Lazy import to keep startup fast for non-audio workflows
        import whisper

        # 1. Find Files
        files = glob.glob(input_pattern)
        if not files:
            logger.warning(f"No audio files found matching: {input_pattern}")
            context.set(output_key, [])
            return context

        logger.info(
            f"Found {len(files)} audio files. Loading Whisper model '{model_size}'..."
        )

        # 2. Load Model
        device = "cuda" if torch.cuda.is_available() else "cpu"
        use_fp16 = device == "cuda"
        logger.info(f"Loading Whisper model '{model_size}' on device: {device.upper()}")

        try:
            model = whisper.load_model(model_size)
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise

        # 3. Transcribe Loop
        results = []
        os.makedirs(output_dir, exist_ok=True)

        for filepath in files:
            filename = os.path.basename(filepath)
            logger.info(f"Transcribing: {filename}...")

            try:
                # The actual heavy lifting
                transcript_result = model.transcribe(filepath, fp16=use_fp16)
                text = transcript_result["text"].strip()

                # Structure matches DirectoryLoader output
                doc_record = {
                    "filename": f"{filename}.txt",  # Rename output to txt
                    "filepath": filepath,
                    "content": text,
                }
                results.append(doc_record)

                # Optional: Save raw transcript
                if save_to_disk:
                    txt_path = os.path.join(output_dir, f"{filename}.txt")
                    with open(txt_path, "w", encoding="utf-8") as f:
                        f.write(text)
                    logger.debug(f"Saved raw transcript: {txt_path}")

            except Exception as e:
                logger.error(f"Error transcribing {filename}: {e}")

        # 4. Update Context
        context.set(output_key, results)
        logger.info(
            f"Transcribed {len(results)} files into context key '{output_key}'."
        )

        return context
