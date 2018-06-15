release: test build
	twine upload dist/*

build:
	pip3 install wheel twine
	python3 setup.py sdist bdist_wheel

clean:
	rm -rf build release dist emanate.egg-info

test:
	tox

.PHONY: release build clean test
