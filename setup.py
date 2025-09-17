#!/usr/bin/env python

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tap-sigma-computing",
    version="0.1.0",
    description="Singer tap for extracting data from Sigma Computing API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/tap-sigma-computing",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="singer tap meltano sigma computing api etl",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.1",
        "singer-python>=5.12.1",
        "click>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ]
    },
    entry_points={
        "console_scripts": [
            "tap-sigma-computing=tap_sigma_computing:main",
        ]
    },
    package_dir={"": "."},
    py_modules=["tap_sigma_computing"],
)
