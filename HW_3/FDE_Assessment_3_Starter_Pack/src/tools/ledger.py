from __future__ import annotations

from src.contracts import EvidenceItem


class EvidenceLedger:
    def __init__(self) -> None:
        self._entries: list[EvidenceItem] = []
        self._counter: int = 1

    def record(self, source: str, finding: str, reference: str | None = None) -> EvidenceItem:
        entry_id = f"E{self._counter}"
        self._counter = self._counter + 1
        ref_text = entry_id
        if reference is not None:
            ref_text = f"{entry_id}: {reference}"
        item = EvidenceItem(
            source=source,
            finding=finding,
            reference=ref_text,
        )
        self._entries.append(item)
        return item

    def get_items(self) -> list[EvidenceItem]:
        return list(self._entries)

    def clear(self) -> None:
        self._entries = []
        self._counter = 1
