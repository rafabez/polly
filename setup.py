"""
Setup script for Polly
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="polly-ai",
    version="0.1.0",
    author="Interzone (Rafael Beznos)",
    author_email="",
    description="Cross-Platform AI Terminal Assistant powered by Pollinations.ai",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rafabez/polly",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Shells",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "polly=polly.__main__:main",
        ],
    },
    keywords="ai assistant terminal cli linux bash pollinations",
    project_urls={
        "Bug Reports": "https://github.com/rafabez/polly/issues",
        "Source": "https://github.com/rafabez/polly",
    },
)
