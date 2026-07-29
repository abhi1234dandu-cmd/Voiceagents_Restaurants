from functools import lru_cache
from typing import Any, Optional

from app.config import get_settings


class InMemoryStore:
    """Fallback store for local/dev when Supabase is not configured."""

    def __init__(self) -> None:
        self.tables: dict[str, list[dict[str, Any]]] = {}

    def table(self, name: str) -> "InMemoryQuery":
        self.tables.setdefault(name, [])
        return InMemoryQuery(self, name)


class InMemoryQuery:
    def __init__(self, store: InMemoryStore, table: str):
        self.store = store
        self.table_name = table
        self._filters: list[tuple[str, str, Any]] = []
        self._data: Optional[dict[str, Any]] = None
        self._op = "select"
        self._limit: Optional[int] = None
        self._order: Optional[tuple[str, bool]] = None
        self._update: Optional[dict[str, Any]] = None
        self._select_cols = "*"

    def select(self, cols: str = "*") -> "InMemoryQuery":
        self._op = "select"
        self._select_cols = cols
        return self

    def insert(self, data: dict[str, Any] | list[dict[str, Any]]) -> "InMemoryQuery":
        self._op = "insert"
        self._data = data if isinstance(data, dict) else data[0]
        return self

    def update(self, data: dict[str, Any]) -> "InMemoryQuery":
        self._op = "update"
        self._update = data
        return self

    def delete(self) -> "InMemoryQuery":
        self._op = "delete"
        return self

    def eq(self, col: str, val: Any) -> "InMemoryQuery":
        self._filters.append(("eq", col, val))
        return self

    def gte(self, col: str, val: Any) -> "InMemoryQuery":
        self._filters.append(("gte", col, val))
        return self

    def lte(self, col: str, val: Any) -> "InMemoryQuery":
        self._filters.append(("lte", col, val))
        return self

    def ilike(self, col: str, val: Any) -> "InMemoryQuery":
        self._filters.append(("ilike", col, val))
        return self

    def limit(self, n: int) -> "InMemoryQuery":
        self._limit = n
        return self

    def order(self, col: str, desc: bool = False) -> "InMemoryQuery":
        self._order = (col, desc)
        return self

    def _match(self, row: dict[str, Any]) -> bool:
        for op, col, val in self._filters:
            rv = row.get(col)
            if op == "eq" and str(rv) != str(val):
                return False
            if op == "gte" and not (rv is not None and rv >= val):
                return False
            if op == "lte" and not (rv is not None and rv <= val):
                return False
            if op == "ilike":
                pattern = str(val).replace("%", "").lower()
                if pattern not in str(rv or "").lower():
                    return False
        return True

    def execute(self) -> Any:
        rows = self.store.tables[self.table_name]
        if self._op == "insert" and self._data is not None:
            rows.append(self._data)
            return type("R", (), {"data": [self._data]})()
        matched = [r for r in rows if self._match(r)]
        if self._op == "update" and self._update is not None:
            for r in matched:
                r.update(self._update)
            return type("R", (), {"data": matched})()
        if self._op == "delete":
            keep = [r for r in rows if not self._match(r)]
            self.store.tables[self.table_name] = keep
            return type("R", (), {"data": matched})()
        if self._order:
            col, desc = self._order
            matched.sort(key=lambda x: x.get(col) or "", reverse=desc)
        if self._limit is not None:
            matched = matched[: self._limit]
        return type("R", (), {"data": matched})()


@lru_cache
def get_memory_store() -> InMemoryStore:
    return InMemoryStore()


@lru_cache
def get_supabase() -> Any:
    settings = get_settings()
    if settings.supabase_url and settings.supabase_service_role_key:
        from supabase import create_client

        return create_client(settings.supabase_url, settings.supabase_service_role_key)
    return get_memory_store()
