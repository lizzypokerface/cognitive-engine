from abc import ABC, abstractmethod
from typing import Dict, Any
from src.core.context import WorkflowContext


class PipelineTask(ABC):
    """
    The atomic unit of work in the Cognitive Engine.
    All components (Extractors, Summarizers, Loaders) must inherit from this.
    """

    @abstractmethod
    def execute(
        self, context: WorkflowContext, config: Dict[str, Any]
    ) -> WorkflowContext:
        """
        Performs the specific task logic.

        Args:
            context: The shared state object containing inputs.
            config: A dictionary of runtime parameters (e.g., paths, model names).

        Returns:
            The modified context object.
        """
        pass
