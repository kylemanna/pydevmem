#!/usr/bin/env python3

import pathlib
from setuptools import setup

# The text of the README file
README = (pathlib.Path(__file__).parent / "README.md").read_text()

setup(
    name="devmem",
    version="0.1.0",
    description="Python devmem clone",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/kylemanna/pydevmem",
    author="Kyle Manna",
    author_email="kyle@kylemanna.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["devmem"],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "pydevmem=devmem:main",
        ]
    },
)

