"""Kiem tra cu phap Legal.schema ma khong can dung server.

`knext schema commit` chi bao loi khi cum Docker da chay va da dang ky du an,
nen mot loi dau ngoac cung bat ta di het vong do. Script nay ap dung dung cac
bieu thuc chinh quy cua knext/schema/marklang/schema_ml.py ngay tai cho.

    python check_schema.py
"""

import io
import os
import re
import sys

NAMESPACE = re.compile(r"^namespace\s+([a-zA-Z0-9]+)$")
TYPE = re.compile(r"^([a-zA-Z0-9\.]+)\((\w+)\):\s*?([a-zA-Z0-9,]+)$")
META = re.compile(
    r"^(desc|properties|relations|hypernymPredicate|regular|spreadable|autoRelate):\s*?(.*)$"
)
PROPERTY = re.compile(r"^([a-zA-Z0-9#]+)\(([\w\.]+)\):\s*?([a-zA-Z0-9,\.]+)$")
SUB = re.compile(r"^(desc|properties|constraint|rule|index):\s*?(.*)$")

VALID_KINDS = {"EntityType", "ConceptType", "EventType", "StandardType"}
BASIC_TYPES = {"Text", "Integer", "Float"}
# muc thut dong: 0 kieu, 5 properties/relations, 8 thuoc tinh, 12 index/constraint
LEVELS = {0: TYPE, 5: META, 8: PROPERTY, 12: SUB}


def check(path):
    types, refs, errors = {}, [], []

    for num, raw in enumerate(io.open(path, encoding="utf-8"), 1):
        line = raw.rstrip("\n")
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        body = line.strip()

        if indent not in LEVELS:
            errors.append("dong %d: thut dong %d la khong hop le" % (num, indent))
            continue
        if indent == 0 and NAMESPACE.match(body):
            continue

        match = LEVELS[indent].match(body)
        if not match:
            errors.append("dong %d: sai cu phap -> %s" % (num, body))
            continue
        if indent == 0:
            types[match.group(1)] = match.group(3)
        elif indent == 8:
            refs.append((num, match.group(3)))

    for name, kind in types.items():
        if kind not in VALID_KINDS:
            errors.append("kieu %s khai la %s, khong hop le" % (name, kind))
    for num, target in refs:
        if target not in BASIC_TYPES and target not in types:
            errors.append("dong %d: tro toi kieu %s chua duoc dinh nghia" % (num, target))

    return types, errors


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    schema = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "Legal.schema")

    types, errors = check(schema)
    print("%s: %d kieu" % (os.path.basename(schema), len(types)))
    for error in errors:
        print("  LOI:", error)
    if errors:
        sys.exit(1)
    print("  cu phap hop le")
