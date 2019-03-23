#!/bin/sh -e

run() {
    echo '$' "$@"
    "$@"
}

# TODO: Check that all packages from lint-requirements are installed?

run flake8 --version
run flake8

echo

run pylint --version
run pylint emanate
