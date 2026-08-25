from abc import ABC, abstractmethod
from ...domain.code_model import SqlFile, CodeModel


class SqlParserPort(ABC):
    @abstractmethod
    def parse_file(self, file_path: str, content: str) -> SqlFile:
        pass

    @abstractmethod
    def parse_code_model(self, paths: list[str]) -> CodeModel:
        pass
