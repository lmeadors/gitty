# working on the project...

This document has 2 purposes - it explains how to work with the project (in case you want to extend it), and it is a 
place for me to add notes so i remember how to do stuff. :|

### building and installing a local test build

You'll want to use one of the master branches for development work - from the project root, you can do this to install 
a development snapshot from your sources:

    git checkout 1.0/master
    pip3 install -e .
   
This is a "live" version - as you make changes to the project, running it will be reflected immediately.

> NOTE: If you update your python after installing a local version, then remove the old version, things may break - to
> fix the problem, run `pip3 install -e .` again.

### building a distribution

If you want to build a release, you'll start on a master branch (i.e., `1.0/master`), then use gitty to snap a release:

    gitty r
    git push --all && git push --tags
    
Next, you want to build the deployment artifact from the matching release branch:
    
    git checkout 1.0/releases

Now, make sure it's a clean build by removing some junk, and do a build:

    rm -rf dist build htmlcov
    python3 setup.py sdist bdist_wheel

Instructions for deploying are below...

### deploying to pypi (test)

    python3 -m twine upload --repository testpypi dist/*

### deploying to pypi (production)

    python3 -m twine upload dist/*

## uninstall and install from pypi

    pip3 uninstall gitty
    pip3 install gitty --no-cache-dir

To install a specific version:

    pip3 install gitty==1.0.3 --no-cache-dir

