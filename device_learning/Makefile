# device_learning 常用命令

.PHONY: ledger test verify phase-b clean status freeze ci health dryrun handoff check-captures readiness

ledger:
	python3 scripts/generate_ledger.py

test:
	python3 -m pytest tests/ -q

verify: ledger
	python3 scripts/verify_completion.py

phase-b:
	python3 scripts/run_phase_b.py

status:
	python3 scripts/print_status.py

handoff:
	python3 scripts/print_handoff.py

check-captures:
	python3 scripts/validate_captures.py

readiness:
	python3 scripts/build_phase_b_readiness.py
	@echo "---"
	@head -20 PHASE_B_READINESS.md

freeze: verify
	@echo "Static phase frozen — see manifests/static_freeze.json"

ci: verify test

dryrun:
	python3 scripts/dryrun_phase_b.py

health:
	python3 scripts/health_check.py

clean:
	rm -rf .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
