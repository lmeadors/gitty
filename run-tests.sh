#!/usr/bin/env zsh
coverage run -m unittest discover
coverage html
open htmlcov/index.html