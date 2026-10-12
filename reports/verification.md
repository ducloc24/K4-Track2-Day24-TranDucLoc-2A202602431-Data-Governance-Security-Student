# Verification

- Python: `3.12.3`.
- Gitleaks: `8.30.1`.
- History scan: `gitleaks git --config .gitleaks.toml --redact .` -> exit `1`, 1 synthetic finding at commit `1bdd849`.
- Current tree scan: `gitleaks dir --config .gitleaks.toml --redact .` -> exit `0`, no finding.
- Dependency install: `python -m pip install --require-hashes -r requirements.lock` -> passed; packages already satisfied from the locked versions.
- Supply-chain tests: `python -m pytest tests/test_supply_chain.py -v --basetemp=.pytest_tmp_supply` -> initially 2 passed, 1 failed because incident report was blank; after filling `reports/secrets-incident.md`, the full suite passed.
- Full suite: `python -m pytest tests/ -q --basetemp=.pytest_tmp_all` -> `33 passed`.
- CP3a: `gold=118 pred=118 tp=118`, precision `1.000`, recall `1.000`.
- CP3d split: `tests/test_split.py` -> `1 passed`; `KH-000777` was never read.
- Injection replay: `tests/test_injection.py` -> `8 passed, 0 skipped`.
- Ledger: `tests/test_ledger.py` -> `3 passed`; `ledger.verify()` -> `True`.
- CP5 command: `python -m agent.loop --mock --as dpo "Tổng hợp các ticket còn mở tuần này"` completed normally.
- `reports/attack-before.log`: 4 POST lines containing synthetic `KH-000999` data.
- `reports/attack-after.log`: `0` bytes.
- After CP5, ledger contains `http_post`, `decision=deny`, `reason=restricted data cannot use egress`, `on_behalf_of=dpo`; verification returned `True`.
- Pre-commit: `pre-commit install` / `pre-commit run --all-files` = `NOT_VERIFIED`; the installed pre-commit cache failed with `sqlite3.OperationalError: attempt to write a readonly database` outside the workspace. The hook configuration itself is covered by `tests/test_supply_chain.py`.
