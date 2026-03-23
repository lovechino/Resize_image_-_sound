import os
from abc import ABC, abstractmethod
from ..config import OptimizerConfig

class BaseOptimizer(ABC):
    def __init__(self, config: OptimizerConfig):
        self.config = config # Dependency Injection

    @abstractmethod
    def optimize(self, input_path: str, output_path: str) -> bool:
        """
        Optimize the asset from input_path and save to output_path.
        Returns True if optimization was successful, False otherwise.
        """
        pass

    def ensure_dir(self, file_path: str):
        """Ensure the directory for the given file path exists."""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
