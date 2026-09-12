# Copyright 2023 OpenSPG Authors
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied.

"""
Builder Dir.
"""

# --- Va loi: KAG bam nat ten thuc the tieng Viet ---------------------------
#
# kag/common/utils.py:196 processing_phrases() thay MOI ky tu ngoai
# [A-Za-z0-9 CJK] bang dau cach. schema_free_extractor.py:424 dung ket qua lam
# CA id LAN name cua node, nen "Luật 116/2025/QH15" thanh "lu t 116 2025 qh15".
# Phia solver khong goi ham nay (cau hoi giu dau) va node nap qua
# external_graph cung khong, nen hai ben khong bao gio gop duoc voi nhau.
#
# Vi sao gan de o CAP MODULE chu khong sua kag.common.utils: to_camel_case()
# goi ban goc qua kag.common.utils va duoc dung o schema_free_extractor.py:358
# de sinh edge_type. Edge type phai thuan ASCII cho server nuot duoc. Gan de
# cap module giu nguyen duong do.
#
# File nay CO chay: indexer.py va injection.py goi
# import_modules_from_path(kag/builder), ham do (kag/common/registry/utils.py:31)
# chen kag/ vao sys.path roi import_module("builder"), tuc chinh file nay,
# duoi ten goi `builder`. Than ham resolve bien global luc goi nen thu tu
# import khong quan trong.
#
# Ghi chu: schema_constraint_extractor va knowledge_unit_extractor cung dung
# processing_phrases, nhung kag_config.yaml dang chay schema_free_extractor
# nen khong va tham o day.
import re as _re

from kag.builder.component.extractor import schema_free_extractor as _sfe


def _processing_phrases_giu_dau(phrase):
    r"""Nhu ban goc nhung giu chu co dau: \w trong che do Unicode."""
    return _re.sub(r"[^\w ]", " ", str(phrase).lower(), flags=_re.U).strip()


_sfe.processing_phrases = _processing_phrases_giu_dau
