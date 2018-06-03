release: build
	twine upload dist/*

build:
	pip3 install wheel twine
	python3 setup.py sdist bdist_wheel

clean:
	rm -rf build release dist emanate.egg-info

.PHONY: release build clean
