"""Setup file"""
from pathlib import Path
from setuptools import setup, find_packages

THIS_DIR = Path(__file__).resolve().parent
README = THIS_DIR / "README.md"

REQUIRES = [
    "beancount",
]

EXTRAS = {"dev": ["black", "pre-commit", "flake8", "readme-renderer"]}

CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    "Natural Language :: English",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
]

setup(
    # Package description.
    name="beancount-db",
    description="Beancount importer for Deutsche Bank account CSV exports.",
    long_description=README.read_text(),
    long_description_content_type="text/markdown",
    author="Sean Leavey",
    author_email="github@attackllama.com",
    url="https://github.com/SeanDS/beancount-db",
    # Versioning.
    use_scm_version={"write_to": "beancount_db/_version.py"},
    # Packages.
    packages=find_packages(),
    zip_safe=False,
    # Requirements.
    python_requires=">=3.6",
    install_requires=REQUIRES,
    setup_requires=["setuptools_scm"],
    extras_require=EXTRAS,
    # Other.
    license="GPL",
    classifiers=CLASSIFIERS,
)
