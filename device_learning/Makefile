# device_learning 常用命令

.PHONY: ledger test verify phase-b clean

ledger:
	python3 scripts/generate_ledger.py

test:
	python3 -m pytest tests/ -q

verify: ledger
	python3 scripts/verify_completion.py

phase-b:
	python3 scripts/run_phase_b.py

clean:
	rm -rf .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
