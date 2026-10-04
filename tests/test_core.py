import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from agents.llm import parse_json
from agents.memory import Memory
from agents.tools import calculator


def test_calculator_basic():
    assert calculator("(120*0.15)+40") == "58.0"


def test_calculator_blocks_code():
    with pytest.raises(Exception):
        calculator("__import__('os').system('ls')")


def test_parse_json_with_fences():
    assert parse_json('```json\n{"a": 1}\n```') == {"a": 1}


def test_memory_roundtrip(tmp_path):
    m = Memory(str(tmp_path / "t.db"))
    m.save("solid state batteries", "Batteries report body")
    assert m.search("batteries")[0]["topic"] == "solid state batteries"
    assert m.search("unrelated cooking") == []
