"TransactDOM"

from typing import Sequence, List, Optional, Tuple, TypeVar

from .filedom import FileDOM
from .schema import SchemaDOM

DOM = TypeVar("DOM", bound="TransactDOM")


class TransactDOM():
    """Parses a transaction file"""

    def __init__(self,
                 text: Optional[Sequence[str]] = None):
        self.valid = False
        self.files = []  # type: List[FileDOM]
        self.schemas = []
        self.delete = []  # type: List[Tuple[str, str]]
        self.mntner = None  # type: Optional[str]

        if text is not None:
            self.parse(text)

    def parse(self, text: Sequence[str]):
        "parse text"

        buffer = []  # type: List[str]
        for (i, line) in enumerate(text, 1):
            _ = i

            if self.mntner is None:
                if not line.startswith(".BEGIN"):
                    continue

                fields = line.split()

                if len(fields) < 2:
                    continue

                self.mntner = fields[1]
                continue

            if line.startswith("."):
                if len(buffer) > 0:
                    dom = FileDOM(text=buffer)
                    buffer = []
                    if dom.valid:
                        self.files.append(dom)

                        if dom.schema == 'schema':
                            self.schemas.append(SchemaDOM(dom))

                if line.startswith(".DELETE"):
                    sp = line.split()
                    if len(sp) > 2:
                        self.delete.append((sp[1], sp[2]))

                continue

            buffer.append(line)

    def __str__(self) -> str:
        s = f".BEGIN {self.mntner}\n"
        s += "\n".join({f"DELETE {i}" for i in self.delete})
        s += "...\n".join({str(record) for record in self.files})
        s += ".END"
        return s

    @staticmethod
    def from_file(src: str) -> DOM:
        "Read transact from files"
        with open(src) as f:
            return TransactDOM(f.readlines())