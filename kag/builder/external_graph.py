# -*- coding: utf-8 -*-
"""Loader do thi ngoai cho metadata van ban.

Vi sao khong dung thang DefaultExternalGraphLoader: ham __init__ cua no kiem
tra thuoc tinh bang `k not in self.schema[node.label]`, ma BaseSpgType khong
dinh nghia __contains__ / __iter__ nen dong do nem TypeError ngay khi node co
bat ky thuoc tinh nao. Vi du domain_kg cua KAG khong dinh vi loi nay vi moi
node cua no deu co properties rong.

Cach xu ly: tam go properties ra truoc khi goi super(), roi tu kiem tra lai
bang spg_type.properties (cai nay co that) va gan tra ve.
"""

from typing import List

from kag.interface import ExternalGraphLoaderABC, MatchConfig
from kag.builder.component.external_graph.external_graph import (
    DefaultExternalGraphLoader,
)
from kag.builder.model.sub_graph import Node, Edge


@ExternalGraphLoaderABC.register("legal_external_graph", constructor="from_json_file")
class LegalExternalGraphLoader(DefaultExternalGraphLoader):
    def __init__(
        self, nodes: List[Node], edges: List[Edge], match_config: MatchConfig, **kwargs
    ):
        saved = [node.properties for node in nodes]
        for node in nodes:
            node.properties = {}

        super().__init__(
            nodes=nodes, edges=edges, match_config=match_config, **kwargs
        )

        for node, properties in zip(self.nodes, saved):
            spg_type = self.schema[node.label]
            unknown = set(properties) - set(spg_type.properties)
            if unknown:
                raise ValueError(
                    f"Node {node.name} co thuoc tinh ngoai schema: {sorted(unknown)}"
                )
            node.properties = properties
