.PHONY: build check lint static-check test verify

PYTHON ?= python3

check: test static-check

verify: check

build: test

lint: static-check

test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover -v

static-check:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -c "import pathlib; [compile(pathlib.Path(path).read_text(), path, 'exec') for path in ('SpoofMACAddress.py', 'test_spoof_mac_address.py', 'scripts/check-baseline.py')]"
	sh -n SpoofMACAddress
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) scripts/check-baseline.py
