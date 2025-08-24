from abc import ABC, abstractmethod
from typing import List
from langchain_core.documents import Document
from fastapi import UploadFile

class IFileRepository(ABC):
    @abstractmethod
    def convert_file_docx(self, file) -> Document:
        pass

    @abstractmethod
    def convert_file_xlsx(self, file) -> Document:
        pass
    
    @abstractmethod
    def convert_file_csv(self, file) -> Document:
        pass
    
    @abstractmethod
    def convert_file_txt(self, file) -> Document:
        pass
    
    @abstractmethod
    def extract_file(self, documents: list[UploadFile]) -> List[Document]:
        pass
