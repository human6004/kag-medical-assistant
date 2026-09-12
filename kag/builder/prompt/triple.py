# -*- coding: utf-8 -*-
"""Trích quan hệ ba ngôi cho văn bản pháp luật Việt Nam.

Extractor dựng cạnh đồ thị từ [chủ ngữ, vị ngữ, tân ngữ]. Vị ngữ để tự do
thì mỗi chunk sinh ra một cách gọi khác nhau và đồ thị vỡ vụn, nên prompt
ép dùng trước bộ vị ngữ trùng tên quan hệ trong Legal.schema.
"""

import json
from typing import List

from kag.interface import PromptABC


TEMPLATE = """
{
    "instruction": "Bạn là chuyên gia trích xuất quan hệ từ văn bản pháp luật Việt Nam. Từ đoạn văn trong trường input, hãy liệt kê mọi quan hệ có thể rút ra dưới dạng bộ ba [chủ ngữ, vị ngữ, tân ngữ] và trả về theo đúng định dạng của trường output trong ví dụ. Yêu cầu: (1) Mỗi bộ ba phải chứa ít nhất một, tốt nhất là hai, thực thể có tên trong entity_list, và viết tên y hệt trong entity_list. (2) Thay mọi đại từ và cách gọi trỏ ngược như 'Điều này', 'Nghị định này' bằng tên cụ thể. (3) ƯU TIÊN dùng đúng các vị ngữ sau khi ý nghĩa khớp, không tự đặt từ đồng nghĩa: 'thuộc văn bản' nối một điều luật với văn bản chứa nó; 'nghiêm cấm' nối điều luật với hành vi vi phạm; 'quy định chế tài' nối điều luật với mức phạt hoặc biện pháp khắc phục; 'quy định nghĩa vụ' nối điều luật với nghĩa vụ; 'định nghĩa' nối điều luật với thuật ngữ pháp lý; 'áp dụng cho' nối điều luật với đối tượng bị điều chỉnh; 'áp dụng cho hành vi' nối một chế tài với hành vi vi phạm bị chế tài đó xử lý; 'căn cứ pháp lý' nối chế tài với điều luật làm căn cứ; 'thẩm quyền xử phạt' nối chế tài với cơ quan có thẩm quyền; 'thay thế', 'bị thay thế bởi', 'sửa đổi bổ sung', 'hướng dẫn thi hành' nối hai văn bản với nhau. (4) Quan hệ nào không nằm trong danh sách trên thì mới đặt vị ngữ tự do, viết ngắn và giữ nguyên động từ của luật. (5) Không suy diễn quan hệ mà đoạn văn không nói. Nếu không có quan hệ nào thì trả về danh sách rỗng. Chỉ trả về một chuỗi JSON, không giải thích thêm.",
    "entity_list": $entity_list,
    "input": "$input",
    "example": {
        "input": "Điều 34. Vi phạm quy định về xác thực, định danh, bảo mật tài khoản số\\n2. Phạt tiền từ 30.000.000 đồng đến 50.000.000 đồng đối với một trong các hành vi sau đây: c) Sử dụng công nghệ trí tuệ nhân tạo (AI), Deepfake hoặc các biện pháp kỹ thuật công nghệ cao để giả mạo dữ liệu sinh trắc học (khuôn mặt, giọng nói) nhằm xác thực tài khoản trái phép.\\n3. Biện pháp khắc phục hậu quả: Buộc khôi phục lại tình trạng ban đầu đối với hành vi vi phạm quy định tại khoản 1, 2 Điều này. Việc xử phạt do lực lượng chuyên trách bảo vệ an ninh mạng thực hiện. Nghị định 330/2026/NĐ-CP quy định chi tiết thi hành Luật An ninh mạng.",
        "entity_list": [
            {"name": "Điều 34 Nghị định 330/2026/NĐ-CP", "category": "Article"},
            {"name": "Nghị định 330/2026/NĐ-CP", "category": "LegalDocument"},
            {"name": "Luật An ninh mạng", "category": "LegalDocument"},
            {"name": "Sử dụng công nghệ trí tuệ nhân tạo (AI), Deepfake để giả mạo dữ liệu sinh trắc học nhằm xác thực tài khoản trái phép", "category": "ProhibitedAct"},
            {"name": "Phạt tiền từ 30.000.000 đồng đến 50.000.000 đồng", "category": "Sanction"},
            {"name": "Buộc khôi phục lại tình trạng ban đầu", "category": "Sanction"},
            {"name": "dữ liệu sinh trắc học", "category": "LegalTerm"},
            {"name": "lực lượng chuyên trách bảo vệ an ninh mạng", "category": "Authority"},
            {"name": "chủ sở hữu tài khoản số", "category": "RegulatedEntity"}
        ],
        "output": [
            ["Điều 34 Nghị định 330/2026/NĐ-CP", "thuộc văn bản", "Nghị định 330/2026/NĐ-CP"],
            ["Điều 34 Nghị định 330/2026/NĐ-CP", "nghiêm cấm", "Sử dụng công nghệ trí tuệ nhân tạo (AI), Deepfake để giả mạo dữ liệu sinh trắc học nhằm xác thực tài khoản trái phép"],
            ["Điều 34 Nghị định 330/2026/NĐ-CP", "quy định chế tài", "Phạt tiền từ 30.000.000 đồng đến 50.000.000 đồng"],
            ["Điều 34 Nghị định 330/2026/NĐ-CP", "quy định chế tài", "Buộc khôi phục lại tình trạng ban đầu"],
            ["Điều 34 Nghị định 330/2026/NĐ-CP", "áp dụng cho", "chủ sở hữu tài khoản số"],
            ["Phạt tiền từ 30.000.000 đồng đến 50.000.000 đồng", "áp dụng cho hành vi", "Sử dụng công nghệ trí tuệ nhân tạo (AI), Deepfake để giả mạo dữ liệu sinh trắc học nhằm xác thực tài khoản trái phép"],
            ["Phạt tiền từ 30.000.000 đồng đến 50.000.000 đồng", "căn cứ pháp lý", "Điều 34 Nghị định 330/2026/NĐ-CP"],
            ["Phạt tiền từ 30.000.000 đồng đến 50.000.000 đồng", "thẩm quyền xử phạt", "lực lượng chuyên trách bảo vệ an ninh mạng"],
            ["Buộc khôi phục lại tình trạng ban đầu", "áp dụng cho hành vi", "Sử dụng công nghệ trí tuệ nhân tạo (AI), Deepfake để giả mạo dữ liệu sinh trắc học nhằm xác thực tài khoản trái phép"],
            ["Nghị định 330/2026/NĐ-CP", "hướng dẫn thi hành", "Luật An ninh mạng"],
            ["Sử dụng công nghệ trí tuệ nhân tạo (AI), Deepfake để giả mạo dữ liệu sinh trắc học nhằm xác thực tài khoản trái phép", "giả mạo", "dữ liệu sinh trắc học"]
        ]
    }
}
"""


@PromptABC.register("legal_triple")
class LegalTriplePrompt(PromptABC):
    template_en = TEMPLATE
    template_zh = TEMPLATE

    @property
    def template_variables(self) -> List[str]:
        return ["entity_list", "input"]

    def parse_response(self, response: str, **kwargs):
        rsp = response
        if isinstance(rsp, str):
            rsp = json.loads(rsp)
        if isinstance(rsp, dict) and "output" in rsp:
            rsp = rsp["output"]
        if isinstance(rsp, dict) and "triples" in rsp:
            triples = rsp["triples"]
        else:
            triples = rsp

        standardized_triples = []
        for triple in triples:
            if isinstance(triple, list):
                standardized_triples.append(triple)
            elif isinstance(triple, dict):
                s = triple.get("subject")
                p = triple.get("predicate")
                o = triple.get("object")
                if s and p and o:
                    standardized_triples.append([s, p, o])

        return standardized_triples
