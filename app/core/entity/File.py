from dataclasses import dataclass
from datetime import datetime

@dataclass
class FileDocument:
    name: str
    content: str
    metadata: dict | None = None