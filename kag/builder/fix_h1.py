# -*- coding: utf-8 -*-
"""Dua so hieu van ban len dong h1 cua tung file trong data/processed.

Vi sao can: extractor ghep passage = chunk.name + "\\n" + chunk.content, ma
chunk.name la duong dan tieu de (h1 / Chuong / Dieu). So hieu hien nam o dong
2, tuc than cua node h1, nen khong chunk Dieu nao nhin thay no. LLM se goi van
ban la "Nghi dinh nay" va node do khong bao gio gop duoc voi node metadata ten
"Nghi dinh 330/2026/ND-CP".

Ten dat vao h1 lay tu dung ham node_name cua metadata_to_graph, de hai ben
khong the lech nhau.

Chay thu:  python kag/builder/fix_h1.py
Ghi that:  python kag/builder/fix_h1.py --write
Chay lai nhieu lan duoc, file da dung dinh dang thi bo qua.
"""

import sys
from pathlib import Path

from metadata_to_graph import ROOT, load_metadata, node_name

# Chi con corpus tieng Viet. Kho tieng Anh da xoa vi de tai chi lam luat VN.
MD_DIRS = [ROOT / "data" / "processed"]
SEP = " — "


def all_md():
    return sorted(q for d in MD_DIRS if d.is_dir() for q in d.rglob("*.md"))


def new_h1(name, title):
    return f"# {name}{SEP}{title}"


def plan():
    metas = {m["doc_id"]: m for m in load_metadata()}
    todo, skipped, orphan = [], [], []

    for path in all_md():
        doc_id = path.name.split("_")[0]
        meta = metas.get(doc_id)
        if not meta:
            orphan.append(path)
            continue
        name = node_name(meta)
        lines = path.read_text(encoding="utf-8").splitlines()
        if not lines or not lines[0].startswith("# "):
            orphan.append(path)
            continue
        old = lines[0]
        title = old[2:].strip()
        if title.startswith(name):
            # da co so hieu o dau, chi can chac chan dung dau phan cach
            skipped.append((path, old))
            continue
        todo.append((path, old, new_h1(name, title)))

    return todo, skipped, orphan


def apply(todo):
    for path, _, new in todo:
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        ending = "\n" if lines[0].endswith("\n") else ""
        lines[0] = new + ending
        path.write_text("".join(lines), encoding="utf-8")


def self_check():
    """Moi h1 phai bat dau bang dung ten node ma metadata_to_graph sinh ra."""
    metas = {m["doc_id"]: m for m in load_metadata()}
    bad = []
    for path in all_md():
        meta = metas.get(path.name.split("_")[0])
        if not meta:
            continue
        name = node_name(meta)
        first = path.read_text(encoding="utf-8").splitlines()[0]
        if not first.startswith(f"# {name}"):
            bad.append((path.name, first[:60]))
    if bad:
        print("[FAIL] h1 khong khop ten node:")
        for n, f in bad:
            print("   ", n, "->", f)
        return 1
    print("[self-check ok] moi h1 deu bat dau bang ten node trong nodes.json")
    return 0


def main():
    write = "--write" in sys.argv
    todo, skipped, orphan = plan()

    for path, old, new in todo:
        print(f"{path.relative_to(ROOT)}")
        print(f"  - {old[:100]}")
        print(f"  + {new[:100]}")
    print(f"\nsua: {len(todo)} | da dung san: {len(skipped)} | bo qua: {len(orphan)}")
    for path in orphan:
        print("   bo qua:", path.name)

    if not write:
        print("\nChay thu. Them --write de ghi that.")
        return 0

    apply(todo)
    print(f"\nDa ghi {len(todo)} file.")
    return self_check()


if __name__ == "__main__":
    sys.exit(main())
