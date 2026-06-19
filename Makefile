.PHONY: build check lint static-check test verify

PYTHON ?= python3
override REPO_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

check: test static-check

verify: check

build: test

lint: static-check

test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover -v -s "$(REPO_ROOT)"

static-check:
	REPO_ROOT="$(REPO_ROOT)" PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -c "import os, pathlib; root = pathlib.Path(os.environ['REPO_ROOT']); [compile((root / path).read_text(), path, 'exec') for path in ('SpoofMACAddress.py', 'test_spoof_mac_address.py', 'scripts/check-baseline.py')]"
	sh -n "$(REPO_ROOT)/SpoofMACAddress"
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) "$(REPO_ROOT)/scripts/check-baseline.py"
