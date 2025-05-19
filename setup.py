"""Setup script for luca_core package."""

from setuptools import find_packages, setup

setup(
    name="luca_core",
    version="0.1.0",
    packages=find_packages(where="."),
    package_dir={"": "."},
    install_requires=[
        "pydantic>=2.0.0",
    ],
    python_requires=">=3.13",
)
