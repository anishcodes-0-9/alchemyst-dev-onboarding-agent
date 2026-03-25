from __future__ import annotations

# Simple in-memory context store
_context_store: dict[str, list[dict]] = {}


class ContextStore:
    async def upload(self, session_id: str, facts: dict) -> bool:
        if session_id not in _context_store:
            _context_store[session_id] = []

        for key, value in facts.items():
            if value and value not in [[], None, False]:
                entry = {
                    "key": key,
                    "value": str(value),
                    "text": f"{key}: {value}"
                }

                existing_keys = [e["key"] for e in _context_store[session_id]]

                if key not in existing_keys:
                    _context_store[session_id].append(entry)
                else:
                    for e in _context_store[session_id]:
                        if e["key"] == key:
                            e["value"] = str(value)
                            e["text"] = f"{key}: {value}"

        return True

    async def search(self, session_id: str, query: str) -> list[str]:
        if session_id not in _context_store:
            return []

        results = [entry["text"] for entry in _context_store[session_id]]
        return results[:5]

    async def delete(self, session_id: str) -> bool:
        if session_id in _context_store:
            del _context_store[session_id]
        return True


# singleton instance
context_store = ContextStore()