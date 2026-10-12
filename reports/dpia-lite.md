# DPIA-lite - mo ta hoc tap, khong phai ho so danh gia tac dong chinh thuc

1. **Du lieu va phan loai:** Ticket la noi dung untrusted co the chua prompt injection. Ho so khach trong `data/customers.json` la du lieu restricted, nhung tat ca gia tri trong repo deu la synthetic. PII text duoc detect va redact truoc khi dua vao phan tom tat.

2. **Muc dich va principal:** `support_l1` chi duoc `search_docs`; `dpo` co the doc customer hop le cho `support-reply`. Principal la fixture trong `data/principals.json`, khong phai xac thuc nguoi that.

3. **Du lieu di qua dau:** Run A goi `search_docs`, lay ticket ID tu ten file. Run B map ID qua `related_tickets`, qua policy roi moi goi `read_customer`. Moi yeu cau tool duoc ghi vao `reports/ledger.jsonl`; `http_post` chi tro sink localhost va bi deny voi restricted + egress.

4. **Da chan/cho phep va gioi han:** `support_l1` bi deny doc private; `dpo` doc customer hop le; ca hai bi deny egress restricted. `reports/attack-before.log` co 4 POST synthetic, con `reports/attack-after.log` la 0 byte. Gioi han con lai: mock LLM, principal gia lap, regex PII khong phai NER, hash chain khong tu phat hien cat dong cuoi, sink chi la localhost va chua co production identity/secret management.
