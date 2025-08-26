"""
Setup script for the S.A.M. Decision Engine.

Enhanced version with aegis-core integration for personality-aware,
policy-enforced, and trace-emitted decisions.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sam-decision-engine",
    version="2.0.0",
    author="BawtL Labs",
    author_email="info@bawtlabs.com",
    description="S.A.M. Decision Engine with aegis-core integration",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/bawtL-Labs/aegis-decision-engine",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.18.0",
        ],
        "monitoring": [
            "prometheus-client>=0.16.0",
            "structlog>=23.0.0",
        ],
        "security": [
            "cryptography>=41.0.0",
            "python-jose>=3.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "sam-decision=sam.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "sam": ["py.typed"],
    },
    zip_safe=False,
    keywords=[
        "ai",
        "decision-making",
        "autonomous",
        "personality",
        "mental-health",
        "maturity",
        "utility",
        "policy",
        "tracing",
        "aegis-core",
    ],
    project_urls={
        "Bug Reports": "https://github.com/bawtL-Labs/aegis-decision-engine/issues",
        "Source": "https://github.com/bawtL-Labs/aegis-decision-engine",
        "Documentation": "https://github.com/bawtL-Labs/aegis-decision-engine/blob/main/README.md",
    },
)