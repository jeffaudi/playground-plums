# Standard libraries
import io
import os
import re
from setuptools import setup, find_packages
from typing import List

# Constants
PATH_ROOT = os.path.dirname(__file__)


def _load_requirements(path_dir: str, file_name: str = "requirements.txt", comment_char: str = "#") -> List[str]:
    """Load requirements from a file."""
    with open(os.path.join(path_dir, file_name), "r") as file:
        lines = [ln.strip() for ln in file.readlines()]
    reqs = []
    for ln in lines:
        # Filer all comments
        if comment_char in ln:
            ln = ln[: ln.index(comment_char)].strip()
        # Skip directly installed dependencies
        if ln.startswith("http"):
            continue
        if ln:  # if requirement is not empty
            reqs.append(ln)

    return reqs


with io.open('plums/__init__.py', 'rt', encoding='utf8') as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read(), re.M).group(1)


setup(
    name='plums',
    version=str(version),
    packages=find_packages(exclude=['tests', 'tests.*', 'docs', 'docs.*']),
    author="Airbus DS GEO",
    author_email="jeffaudi.airbus@gmail.com",
    description="Playground ML Unified Microlib Set: The Playground ML python toolbox package",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.6",    
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    install_requires=_load_requirements(path_dir=os.path.join(PATH_ROOT), file_name="requirements.txt"),
    extras_require={
        "docs": _load_requirements(path_dir=os.path.join(PATH_ROOT, "requirements"), file_name="requirements-docs.txt"),
        "lint": _load_requirements(path_dir=os.path.join(PATH_ROOT, "requirements"), file_name="requirements-lint.txt"),
        "tests": _load_requirements(path_dir=os.path.join(PATH_ROOT, "requirements"), file_name="requirements-tests.txt"),
    },
)
