# -*- coding: utf-8 -*-
"""Kiem tra ba prompt ma khong can cai kag hay chay server.

Bat hai loi hay gap nhat: template khong phai JSON hop le (LLM se tra ve rac)
va category trong vi du khong co trong Legal.schema (extractor day ve Others).

Chay: python kag/builder/prompt/check_prompts.py
"""

import json
import re
import sys
from pathlib import Path
from string import Template

HERE = Path(__file__).resolve().parent
SCHEMA_FILE = HERE.parent.parent / "schema" / "Legal.schema"

DUMMY = {
    "schema": '["Article"]',
    "input": "doan van mau",
    "named_entities": "[]",
    "entity_list": "[]",
}


def schema_types():
    text = SCHEMA_FILE.read_text(encoding="utf-8")
    return set(re.findall(r"^([a-zA-Z0-9\.]+)\(\w+\):", text, re.M))


def extract_template(path):
    src = path.read_text(encoding="utf-8")
    body = src.split('TEMPLATE = """', 1)[1].split('"""', 1)[0]
    return Template(body).safe_substitute(**DUMMY)


def main():
    types = schema_types()
    assert "Article" in types, f"khong doc duoc schema tai {SCHEMA_FILE}"
    ok = True
    for name in ("ner.py", "std.py", "triple.py"):
        path = HERE / name
        try:
            data = json.loads(extract_template(path))
        except json.JSONDecodeError as exc:
            print(f"[FAIL] {name}: template khong phai JSON hop le -> {exc}")
            ok = False
            continue
        used = set(re.findall(r'"category":\s*"([^"]+)"', json.dumps(data)))
        bad = used - types
        if bad:
            print(f"[FAIL] {name}: category khong co trong Legal.schema -> {sorted(bad)}")
            ok = False
        else:
            print(f"[ok]   {name}: JSON hop le, {len(used)} category deu khop schema")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
