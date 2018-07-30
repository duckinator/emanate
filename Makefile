release: test build
	python3 setup.py release

build:
	python3 setup.py build

clean:
	python3 setup.py clean

test:
	tox

.PHONY: release build clean test
