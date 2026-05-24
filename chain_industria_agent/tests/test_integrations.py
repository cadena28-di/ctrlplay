"""Tests de integraciones base."""

import json
import tempfile
from pathlib import Path

from src.integrations.memory.store import LocalMemoryStore
from src.integrations.search.client import SearchClient


def test_local_memory_store_save_and_search():
    with tempfile.TemporaryDirectory() as tmp:
        index = Path(tmp) / "index.json"
        store = LocalMemoryStore(index)
        store.save("Chain Industria es un agente modular", entry_type="fact", concepts=["chain"])
        store.log_search("mercado industrial", ["web"], {"total": 3})
        results = store.search("Chain")
        assert len(results) >= 1
        searches = store.get_search_index()
        assert len(searches) == 1
        assert searches[0]["metadata"]["query"] == "mercado industrial"


def test_search_mock_without_api_key():
    client = SearchClient()
    result = client.search("Chain Industria")
    assert result.success
    assert result.provider == "mock"
    assert result.data["results_found"] >= 1


def test_memory_index_file_format():
    with tempfile.TemporaryDirectory() as tmp:
        index = Path(tmp) / "index.json"
        store = LocalMemoryStore(index)
        store.save("test")
        data = json.loads(index.read_text(encoding="utf-8"))
        assert isinstance(data, list)
        assert data[0]["type"] == "fact"
