#!/usr/bin/env python3
"""
Setup script for Personal Finance Tracker

This setup.py file allows the project to be installed as a Python package,
demonstrating understanding of Python packaging and distribution.
"""

from setuptools import setup, find_packages
import pathlib

# Read the README file
HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="personal-finance-tracker",
    version="1.0.0",
    description="A comprehensive personal finance management application with data analytics",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/personal-finance-tracker",
    author="Your Name",
    author_email="your.email@example.com",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial :: Accounting",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    keywords="finance budget tracker analytics visualization",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.5.0",
        "matplotlib>=3.6.0",
        "seaborn>=0.12.0",
        "numpy>=1.24.0",
        "requests>=2.28.0",
        "python-dateutil>=2.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
        ],
        "excel": [
            "openpyxl>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "finance-tracker=finance_tracker:demo_application",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/yourusername/personal-finance-tracker/issues",
        "Source": "https://github.com/yourusername/personal-finance-tracker",
        "Documentation": "https://github.com/yourusername/personal-finance-tracker/wiki",
    },
)

