# working on the project...

This document has 2 purposes - it explains how to work with the project (in case you want to extend it), and it is a 
place for me to add notes so i remember how to do stuff. :|

### building and installing a local test build

From the project root, you can do this to install a development snapshot from your sources:

    pip3 install -e .
   
This is a "live" version - as you make changes to the project, running it will be reflected immediately.

### building a distribution

    rm -rf dist
    python3 setup.py sdist bdist_wheel

### deploying to pypi (test)

    python3 -m twine upload --repository testpypi dist/*

### deploying to pypi (production)

    python3 -m twine upload dist/*
