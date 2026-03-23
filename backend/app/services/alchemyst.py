from __future__ import annotations
from typing import Optional

# In-memory context store — simulates Alchemyst Context API
# When you have an Alchemyst API key, replace this entire class with
# real httpx calls to https://api.getalchemystai.com/context
_context_store: dict[str, list[dict]] = {}


class AlchemystClient:
    """
    Simulates Alchemyst Context API for local development.
    Interface is identical to the real API — swap internals when key is available.
    """

    async def upload(self, session_id: str, facts: dict) -> bool:
        """Store extracted facts for a session."""
        if session_id not in _context_store:
            _context_store[session_id] = []

        # store each non-null fact as a separate searchable document
        for key, value in facts.items():
            if value and value not in [[], None, False]:
                entry = {
                    "key": key,
                    "value": str(value),
                    "text": f"{key}: {value}"
                }
                # avoid duplicates
                existing_keys = [e["key"] for e in _context_store[session_id]]
                if key not in existing_keys:
                    _context_store[session_id].append(entry)
                else:
                    # update existing
                    for e in _context_store[session_id]:
                        if e["key"] == key:
                            e["value"] = str(value)
                            e["text"] = f"{key}: {value}"

        return True

    async def search(self, session_id: str, query: str) -> list[str]:
        """Retrieve relevant stored facts for a session."""
        if session_id not in _context_store:
            return []

        query_lower = query.lower()
        results = []

        for entry in _context_store[session_id]:
            # simple relevance — return all stored facts, most recent first
            results.append(entry["text"])

        return results[:5]

    async def delete(self, session_id: str) -> bool:
        """Clear all context for a session."""
        if session_id in _context_store:
            del _context_store[session_id]
        return True


# singleton instance — import this everywhere
alchemyst = AlchemystClient()