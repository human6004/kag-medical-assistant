# -*- coding: utf-8 -*-
"""Nap metadata van ban (node + canh) thang vao do thi.

Chay tu THU MUC GOC project, sau khi da `knext schema commit`:
    python kag/builder/metadata_to_graph.py
    python kag/builder/injection.py

Chay lai duoc nhieu lan: writer ghi de theo id node nen khong sinh ban sao.
"""

import logging
import os

from kag.common.registry import import_modules_from_path
from kag.interface import KAGBuilderChain

logger = logging.getLogger(__name__)


def inject():
    from kag.common.conf import KAG_CONFIG

    chain = KAGBuilderChain.from_config(
        KAG_CONFIG.all_config["metadata_inject_chain"]
    )
    chain.invoke(None)
    logger.info("\n\nDa nap metadata van ban vao do thi\n\n")


if __name__ == "__main__":
    import_modules_from_path(os.path.dirname(os.path.abspath(__file__)))
    inject()
