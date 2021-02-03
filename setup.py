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


with io.open('playground_plums/__init__.py', 'rt', encoding='utf8') as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read(), re.M).group(1)


setup(
    name='playground-plums',
    version=str(version),
    packages=find_packages(exclude=['tests', 'tests.*', 'docs', 'docs.*']),
    author="Clement Maliet",
    author_email="clement.maliet@magellium.fr",
    description="Playground ML Unified Microlib Set: The Playground ML python toolbox package",
    license="TBD",
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Private :: Do Not Upload to pypi server',
    ],
    install_requires=_load_requirements(path_dir=os.path.join(PATH_ROOT), file_name="requirements.txt"),
    extras_require={
        "docs": _load_requirements(path_dir=os.path.join(PATH_ROOT, "requirements"), file_name="requirements-docs.txt"),
        "lint": _load_requirements(path_dir=os.path.join(PATH_ROOT, "requirements"), file_name="requirements-lint.txt"),
        "tests": _load_requirements(path_dir=os.path.join(PATH_ROOT, "requirements"), file_name="requirements-tests.txt"),
    },
)
