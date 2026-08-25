from abc import ABC, abstractmethod
from typing import List, Optional
from ...domain.detection import DetectionReport
from ...domain.code_model import CodeModel
from ...domain.rules.base import Rule


class PatternDetectorPort(ABC):
    @abstractmethod
    def detect(self, model: CodeModel, custom_rules: Optional[List[Rule]] = None) -> DetectionReport:
        pass
