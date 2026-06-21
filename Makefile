ifneq ($(origin MAKEFILE_LIST),file)
$(error MAKEFILE_LIST must not be overridden)
endif
override REPO_ROOT := $(shell path='$(subst ','"'"',$(MAKEFILE_LIST))'; path=$$(printf '%s' "$$path" | /usr/bin/sed 's/^ //'); directory=$$(/usr/bin/dirname -- "$$path"); CDPATH= cd -- "$$directory" && /bin/pwd -P)
override SHELL_REPO_ROOT := '$(subst ','"'"',$(REPO_ROOT))'

PYTHON ?= python3
.PHONY: build check lint root-test static-check test verify

check: test static-check root-test

verify: check

build: test

lint: static-check

test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover -v -s $(SHELL_REPO_ROOT)

static-check:
	REPO_ROOT=$(SHELL_REPO_ROOT) PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -c "import os, pathlib; root = pathlib.Path(os.environ['REPO_ROOT']); [compile((root / path).read_text(), path, 'exec') for path in ('SpoofMACAddress.py', 'test_spoof_mac_address.py', 'scripts/check-baseline.py')]"
	sh -n $(SHELL_REPO_ROOT)/SpoofMACAddress
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) $(SHELL_REPO_ROOT)/scripts/check-baseline.py

root-test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) $(SHELL_REPO_ROOT)/scripts/test-makefile-root.py
