.PHONY: check test static-check

check: test static-check

test:
	python3 -m unittest discover -v

static-check:
	python3 -m py_compile SpoofMACAddress.py test_spoof_mac_address.py scripts/check-baseline.py
	sh -n SpoofMACAddress
	python3 scripts/check-baseline.py
