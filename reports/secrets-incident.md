# Secret gia trong lich su Git - CP4

- Scanner va phien ban: Gitleaks v8.30.1.
- Commit chua token gia: `1bdd849`.
- File, rule va ket qua quet lich su: Gitleaks history scan voi `.gitleaks.toml` phat hien 1 finding, rule `lab24-synthetic-token`; lenh du kien exit 1. Token duoc redact, khong ghi lai gia tri.
- Ket qua quet file hien tai: `gitleaks dir --config .gitleaks.toml --redact .` sach, exit 0.
- Neu day la credential that: thu hoi/revoke va rotate tai dich vu cap token, kiem tra viec su dung sai, sau do xu ly moi ban sao trong repo, artifact va log.
- Xoa file khoi HEAD hoac pin dependency khong du: token trong lich su Git van co the bi lay lai, nen phai revoke/rotate tai noi cap token.
