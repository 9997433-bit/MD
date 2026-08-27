# device_learning 常用命令

.PHONY: ledger test verify phase-b phase-c clean status freeze ci health dryrun dryrun-usb handoff check-captures readiness closure bundle intake resume finalize proposals help

help:
	@echo "device_learning — 常用命令"
	@echo ""
	@echo "  静态/验收"
	@echo "    make verify      生成账本 + 验收"
	@echo "    make test        pytest"
	@echo "    make ci          verify + test"
	@echo "    make health      包健康检查"
	@echo "    make finalize    ci + health + closure + bundle"
	@echo "    make closure     静态关闭摘要"
	@echo "    make status      一行状态"
	@echo ""
	@echo "  实机（需硬件）"
	@echo "    make intake      分步接入向导"
	@echo "    make resume      Agent 恢复 JSON"
	@echo "    make handoff     人类交接摘要"
	@echo "    make check-captures  采集预检"
	@echo "    make phase-b     采集后刷新账本"
	@echo "    make proposals   升级建议（人工审阅）"
	@echo "    make phase-c     实验日志处理"
	@echo ""
	@echo "  其他"
	@echo "    make dryrun      合成 EEPROM 流水线演练（非实机）"
	@echo "    make dryrun-usb  合成 USB 抓包演练（非实机）"
	@echo "    make bundle      handoff_bundle + pr_body_snapshot"
	@echo "    make readiness   阶段 B 就绪报告"

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

dryrun-usb:
	python3 scripts/dryrun_usb.py

health:
	python3 scripts/health_check.py

clean:
	rm -rf .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
