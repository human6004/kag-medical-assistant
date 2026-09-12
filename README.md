# kag-legal-assistant

Trợ lý hỏi đáp luật an ninh mạng và truyền thông Việt Nam, dựng bằng KAG
(Knowledge-Augmented Generation) của OpenSPG, so sánh với một nền HybridRAG.

## Thư mục

```
docker/     hạ tầng: file compose dựng OpenSPG server, Neo4j, MySQL, MinIO
kag/        dự án KAG, namespace Legal
hybridRAG/  nền so sánh, chạy độc lập, không liên quan tới kag/
```

**Mã nguồn KAG không nằm trong repo này.** Nó là thư viện Python cài riêng, xem
bước 2 dưới đây. Thư mục `kag/` chỉ chứa cấu hình, schema và dữ liệu của dự án.

```
kag/
├── kag_config.yaml        khai API key, namespace, model
├── schema/Legal.schema    khuôn node và cạnh, phải trùng tên namespace
├── builder/
│   ├── indexer.py         dựng đồ thị
│   └── data/              bỏ file .md của bạn vào đây
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

**5. Dựng đồ thị.** Bỏ **một** file `.md` vào `kag/builder/data/` rồi chạy trong
thư mục đó. Mỗi văn bản là một lần tốn tiền gọi AI, nên chạy thử một file, thấy
node hiện trên giao diện web rồi mới bỏ nốt phần còn lại.

```bash
python indexer.py
```

**6. Hỏi.** Sửa `kag/solver/data/questions.json` theo bộ câu hỏi của bạn, rồi
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
