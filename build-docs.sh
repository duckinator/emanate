#!/bin/sh

env PYTHONPATH=./ pdoc3 --html --output-dir ./html --force emanate
