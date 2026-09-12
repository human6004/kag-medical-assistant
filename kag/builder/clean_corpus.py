# -*- coding: utf-8 -*-
"""Don hai loi dinh dang trong corpus markdown.

1. Bieu mau trong phu luc bi viet thanh heading "#### Điều ..." nen reader coi
   chung la dieu luat that. Vi du "Điều 1. Cho phép ……………. (3) được kinh doanh".
   Chung sinh ra thuc the Dieu gia toan dau cham lung. Ha xuong thanh van ban
   thuong, giu nguyen chu.

2. Moc phu luc ("Phụ lục I - Mẫu số 01", "Mẫu số 03") dang la van ban thuong nen
   ca phan phu luc dinh vao Dieu cuoi cung truoc no. O 332/2026/ND-CP dieu nay
   tao ra mot khoi 49.630 ky tu. Nang chung len heading h4 de moi bieu mau la
   mot chunk rieng, ten ro rang.

Ngoai ra xoa ky tu BOM (U+FEFF) lac giua than file.

Chay thu:  python kag/builder/clean_corpus.py
Ghi that:  python kag/builder/clean_corpus.py --write
"""

import re
import sys

from fix_h1 import all_md

# heading Dieu cua bieu mau: co dau cham lung hoac chuoi dau cham dai
FORM_HEADING = re.compile(r"^(#{1,6}\s*)(Điều\b.*(?:…|\.{4,}).*)$", re.M)

# dong chi la moc phu luc, dung mot minh tren dong
ANNEX_MARK = re.compile(
    r"^[ \t]*((?:Phụ lục\s+[IVXLC]+\s*[-–]\s*)?Mẫu số\s+\S+|Phụ lục\s+[IVXLC]+)[ \t]*$",
    re.M,
)

# moc nam sat nhau la muc luc phu luc, khong phai than bieu mau
MIN_BODY = 800


def demote_form_headings(text):
    return FORM_HEADING.subn(lambda m: m.group(2), text)


HEADING = re.compile(r"^#{1,6} ", re.M)


def promote_annex_marks(text):
    marks = [(m.start(), m.end(), m.group(1)) for m in ANNEX_MARK.finditer(text)]
    # Ranh gioi la heading HOAC moc phu luc. Tinh ca heading thi sau khi nang,
    # moc vua nang van con la ranh gioi, nen chay lai cho ket qua y het.
    bounds = sorted([m.start() for m in HEADING.finditer(text)] + [m[0] for m in marks])
    keep = []
    for start, end, name in marks:
        nxt = next((b for b in bounds if b > start), len(text))
        if nxt - start > MIN_BODY:
            keep.append((start, end, name))
    for start, end, name in reversed(keep):
        text = text[:start] + f"#### {name}" + text[end:]
    return text, len(keep)


def clean(text):
    n_bom = text.count("﻿")
    text = text.replace("﻿", "")
    text, n_form = demote_form_headings(text)
    text, n_mark = promote_annex_marks(text)
    return text, (n_bom, n_form, n_mark)


def main():
    write = "--write" in sys.argv
    total = [0, 0, 0]
    touched = 0

    for path in all_md():
        old = path.read_text(encoding="utf-8")
        new, counts = clean(old)
        if new == old:
            continue
        touched += 1
        total = [a + b for a, b in zip(total, counts)]
        print(
            "%-56s BOM=%d  heading bieu mau ha=%d  moc phu luc nang=%d"
            % (path.name[:56], *counts)
        )
        if write:
            path.write_text(new, encoding="utf-8")

    print(
        "\nfile sua: %d | BOM xoa: %d | heading bieu mau ha: %d | moc phu luc nang: %d"
        % (touched, *total)
    )
    if not write:
        print("Chay thu. Them --write de ghi that.")
        return 0
    return self_check()


def self_check():
    """Sau khi don: khong con heading Dieu bieu mau, va chay lai khong doi gi nua."""
    bad = []
    for path in all_md():
        text = path.read_text(encoding="utf-8")
        if "﻿" in text:
            bad.append((path.name, "con BOM"))
        if FORM_HEADING.search(text):
            bad.append((path.name, "con heading Dieu bieu mau"))
        again, _ = clean(text)
        if again != text:
            bad.append((path.name, "chay lai van con doi -> khong on dinh"))
    if bad:
        print("[FAIL]")
        for n, why in bad:
            print("   ", n, "->", why)
        return 1
    print("[self-check ok] sach BOM, khong con heading bieu mau, chay lai khong doi")
    return 0


if __name__ == "__main__":
    sys.exit(main())
