# kag-legal-assistant

Trợ lý hỏi đáp luật an ninh mạng và truyền thông Việt Nam, dựng bằng KAG
(Knowledge-Augmented Generation) của OpenSPG, so sánh với một nền HybridRAG.

## Thư mục

```
data/       kho văn bản luật, dùng chung cho cả hai bên
docker/     hạ tầng: file compose dựng OpenSPG server, Neo4j, MySQL, MinIO
kag/        dự án KAG, namespace Legal
hybridRAG/  nền so sánh, chạy độc lập, không liên quan tới kag/
```

Kho dữ liệu nằm một chỗ duy nhất và cả hai bên cùng đọc từ đó, nên không sợ lệch
bản. 46 văn bản đã làm sạch, nhưng chỉ 23 văn bản tiếng Việt được index. 23 văn
bản quốc tế nằm ở `reference_en/`, không engine nào đọc.

Lý do tách: câu hỏi là tiếng Việt và đáp án phải là điều khoản Việt Nam, trong khi
nửa tiếng Anh chiếm 58% số ký tự. Trộn chung thì thực thể hai ngôn ngữ không gộp
được, đồ thị vỡ đôi và chi phí gọi AI tăng gấp 2,4 lần. Các văn bản quốc tế vẫn có
mặt trong đồ thị dưới dạng node văn bản, nạp từ `metadata/`, chỉ là không có chunk
nội dung.

```
data/
├── processed/     23 file .md luật Việt Nam, đây là thứ cả hai engine đọc
├── reference_en/  23 file .md luật quốc tế, để đối chiếu, KHÔNG index
├── graph/         nodes.json và edges.json sinh từ metadata, nạp thẳng vào đồ thị
├── raw/           bản gốc pdf, docx, html. Không đưa vào git vì nặng 59MB
├── metadata/      50 file json mô tả từng văn bản
├── README.md    quy tắc đặt tên và cấu trúc dữ liệu
└── SOURCES.md   danh sách nguồn đã thẩm định
```

**Mã nguồn KAG không nằm trong repo này.** Nó là thư viện Python cài riêng, xem
bước 2 dưới đây. Thư mục `kag/` chỉ chứa cấu hình, schema và dữ liệu của dự án.

```
kag/
├── kag_config.yaml        khai API key, namespace, model
├── schema/Legal.schema    khuôn node và cạnh, phải trùng tên namespace
├── builder/
│   └── indexer.py         dựng đồ thị, đọc từ data/processed
└── solver/
    ├── eval.py            chạy hỏi đáp và ghi benchmark.txt
    └── data/questions.json  bộ câu hỏi để chấm
```

## Chạy

**1. Dựng hạ tầng.** Cần Docker Desktop đang chạy.

```bash
docker compose -f docker/docker-compose-west.yml up -d
```

Mở `http://127.0.0.1:8887`, đăng nhập `openspg` / `openspg@kag`. Thấy giao diện
là xong bước này. Giao diện sẽ trống, đúng như vậy.

**2. Cài KAG.** Cần Python 3.10, vì `requirements.txt` của KAG ghim
`protobuf==3.20.1` và bản đó không có sẵn cho Python mới hơn.

```bash
py -3.10 -m venv .venv
```

```bash
.venv/Scripts/pip install -e D:/study/học/KAG
```

**3. Điền hai API key** trong `kag/kag_config.yaml`. `openie_llm` và `chat_llm`
là model sinh chữ, `vectorize_model` là model nhúng vector. Cả ba đang để
`api_key: key`, là chỗ điền tạm. Thiếu key vector thì bước 4 dừng ngay.

**4. Đăng ký dự án lên server.** Chạy trong thư mục `kag/`.

```bash
knext project restore --host_addr http://127.0.0.1:8887 --proj_path .
```

Lệnh này tự ghi lại số hiệu dự án vào `kag_config.yaml`, và thử gọi cả hai model
trước khi cho đi tiếp.

```bash
knext schema commit
```

**5. Dựng đồ thị.** Chạy trong thư mục `kag/builder/`. Lệnh này đọc 23 văn bản
tiếng Việt trong `data/processed/`.

Chạy thử một file trước đã. Mỗi văn bản là một lần tốn tiền gọi AI, và 23 văn bản
là hơn 1,7 triệu chữ. Cách rẻ nhất để thử: tạm đổi dòng cuối `indexer.py` trỏ vào
một thư mục con chứa đúng một file, thấy node hiện trên giao diện web rồi mới trỏ
lại `data/processed`.

```bash
python indexer.py
```

**6. Nạp metadata vào đồ thị.** Bước này đưa ngày hiệu lực, trạng thái còn hay hết
hiệu lực, và chuỗi thay thế giữa các văn bản vào đồ thị. Scanner chỉ nhận `.md` nên
đây là đường duy nhất. Chạy từ thư mục gốc project.

```bash
python kag/builder/metadata_to_graph.py && python kag/builder/injection.py
```

**7. Hỏi.** Sửa `kag/solver/data/questions.json` theo bộ câu hỏi của bạn, rồi
chạy trong thư mục `solver/`.

```bash
python eval.py
```

Kết quả ghi ra `benchmark.txt`.

## Ghi chú

- `docker compose stop` để tắt mà giữ đồ thị. `down -v` là xóa sạch, mất luôn số
  tiền AI đã tiêu để dựng.
- `kag_config.yaml` đang để `language: en` và dùng bộ prompt tiếng Anh mặc định.
  Đây là chỗ đầu tiên đáng chỉnh khi muốn chất lượng trích xuất tốt hơn trên văn
  bản tiếng Việt.
- Đổi schema thì phải chạy lại `knext schema commit`. Đổi prompt hay đổi cách
  cắt văn bản thì không cần, server không hề hay biết.
