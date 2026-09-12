# -*- coding: utf-8 -*-
"""Kiem tra duong dan tieu de trong corpus la duy nhat.

Vi sao can: markdown_reader.py:663 va 676 lay
    full_title = " / ".join(current_titles)
    id = generate_hash_id(full_title)
Id khong mang gi phan biet file hay vi tri, nen hai nhanh cung duong dan sinh
cung id va writer upsert de mat mot chunk.

KHONG import kag: moi truong chi co Python 3.14 ma goi kag pin protobuf doi
3.10. Dung lai duong dan bang regex va mot stack theo cap heading, dung cach
markdown_reader.py:489-495 nuoi stack cua no.

Chay: python kag/builder/check_title_paths.py
"""

import sys
from collections import defaultdict

from clean_corpus import HEADING, title_paths
from fix_h1 import ROOT, all_md


def self_check():
    loi = []
    tong_heading = 0

    for ten, con in [("data/processed", "processed")]:
        paths = defaultdict(list)
        n_heading = 0
        for path in all_md():
            if con not in str(path):
                continue
            text = path.read_text(encoding="utf-8")
            n_heading += len(HEADING.findall(text))
            for p in title_paths(text):
                paths[p].append(f"{path.relative_to(ROOT)}")
        trung = {k: v for k, v in paths.items() if len(v) > 1}
        tong_heading += n_heading
        print(f"{ten:22s} heading: {n_heading:5d} | duong dan: {len(paths):5d} | trung: {len(trung)}")
        for k, v in trung.items():
            loi.append(f"{ten}: trung {len(v)} lan -> {k[:90]} ({v[0]})")

    # So heading dem bang regex phai bang so duong dan sinh ra: moi heading dung
    # dung mot duong dan. Lech tuc la co heading bi bo qua hoac dem hai lan.
    n_path = sum(len(title_paths(p.read_text(encoding="utf-8"))) for p in all_md())
    print(f"tong heading: {tong_heading} | tong duong dan sinh ra: {n_path}")
    if n_path != tong_heading:
        loi.append(f"heading {tong_heading} != duong dan {n_path}")

    if loi:
        print("[FAIL]")
        for m in loi:
            print("   ", m)
        return 1
    print("[self-check ok] duong dan tieu de duy nhat trong data/processed")
    return 0


if __name__ == "__main__":
    sys.exit(self_check())
