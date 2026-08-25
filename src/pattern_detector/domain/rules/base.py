from abc import ABC, abstractmethod
from typing import List
from ..code_model import CodeModel
from ..detection import Detection


class Rule(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def evaluate(self, model: CodeModel) -> List[Detection]:
        pass
