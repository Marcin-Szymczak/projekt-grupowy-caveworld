#!/bin/bash
sphinx-apidoc -o build .
sphinx-build -b html . ./build
