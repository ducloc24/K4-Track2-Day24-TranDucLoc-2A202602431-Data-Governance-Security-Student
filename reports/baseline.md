# Baseline - checkpoint 1

1. Baseline chua tao hoac kiem tra `agent_id`, `run_id` hay danh tinh nguoi dung truoc khi goi tool. `_naive_loop()` di thang tu `search_docs` o `agent/loop.py:31` den cac tool; `agent/loop.py:57-58` co `principal_id` cho API moi nhung baseline khong su dung no.

2. Khong co policy kiem muc dich, quyen hoac loai du lieu truoc `http_post`. Sau khi `find_injection()` tra ve chi thi, payload tu tai lieu quyet dinh `customer_id` va `target_url`; baseline goi `read_customer()` o `agent/loop.py:37-40` roi goi `http_post()` o `agent/loop.py:42-44`.

3. Body duoc tao trong loi goi `tools.http_post(injected.target_url, {"records": collected})` tai `agent/loop.py:44`. `agent/tools.py:68-85` chi gioi han URL toi `127.0.0.1:10024` roi gui request; sink ghi body nhan duoc vao `reports/sink.log`.
