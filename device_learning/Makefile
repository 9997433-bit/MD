# device_learning 常用命令

.PHONY: ledger test verify phase-b phase-c clean status freeze ci health dryrun handoff check-captures readiness closure bundle intake resume finalize proposals

ledger:
	python3 scripts/generate_ledger.py

test:
	python3 -m pytest tests/ -q

verify: ledger
	python3 scripts/verify_completion.py

phase-b:
	python3 scripts/run_phase_b.py

phase-c:
	python3 scripts/run_phase_c.py

status:
	python3 scripts/print_status.py

handoff:
	python3 scripts/print_handoff.py

intake:
	python3 scripts/print_intake.py

resume:
	python3 scripts/agent_resume.py

proposals:
	python3 scripts/print_proposals.py

check-captures:
	python3 scripts/validate_captures.py

readiness:
	python3 scripts/build_phase_b_readiness.py
	@echo "---"
	@head -20 PHASE_B_READINESS.md

closure:
	python3 scripts/build_static_closure.py
	@echo "---"
	@head -24 STATIC_CLOSURE.md

bundle:
	python3 scripts/build_handoff_bundle.py

finalize: ci health closure bundle
	@echo "Static package finalized. See STATIC_CLOSURE.md and manifests/handoff_bundle.json"

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
