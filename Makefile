.PHONY: build check lint static-check test verify

check: test static-check

verify: check

build: test

lint: static-check

test:
	python3 -m unittest discover -v

static-check:
	python3 -m py_compile SpoofMACAddress.py test_spoof_mac_address.py scripts/check-baseline.py
	sh -n SpoofMACAddress
	python3 scripts/check-baseline.py
