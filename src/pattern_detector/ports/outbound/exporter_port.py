from abc import ABC, abstractmethod
from ...domain.detection import DetectionReport


class ExporterPort(ABC):
    @abstractmethod
    def export(self, report: DetectionReport, output_path: str) -> None:
        pass
