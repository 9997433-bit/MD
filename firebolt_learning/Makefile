.PHONY: help verify test status ledger clean

help:
	@echo "Firebolt learning package"
	@echo "  make verify  - scan firmware, generate ledger, run tests"
	@echo "  make ledger  - generate EvidenceLedger + manifests only"
	@echo "  make test    - pytest"
	@echo "  make status  - print coverage summary"

ledger:
	python3 scripts/generate_ledger.py

test:
	python3 -m pytest -q tests

verify: ledger test
	@python3 -c "import json; c=json.load(open('coverage.json')); print('coverage', c['identifier_count'], c['by_status'])"

status:
	@python3 -c "import json; from pathlib import Path; c=json.loads(Path('coverage.json').read_text()); print(json.dumps(c, indent=2, ensure_ascii=False))"

clean:
	rm -f EvidenceLedger.json coverage.json ARCHITECTURE.md
	rm -f manifests/manifest_files.json manifests/file_hashes.json
	rm -f manifests/firmware_meta.json manifests/bitstream_meta.json
	rm -f manifests/photo_index.json manifests/system_map.json
