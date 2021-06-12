import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gitty",
    version="1.4.0",
    author="Larry Meadors",
    author_email="larry.meadors@elm-software.com",
    description="An alternate git workflow tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lmeadors/gitty",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    scripts=['bin/gitty', 'bin/_gitty_completion.zsh'],
)
