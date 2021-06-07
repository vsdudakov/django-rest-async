import os
import re

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def get_version(package):
    init_py = open(os.path.join(package, "__init__.py")).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


version = get_version("django_rest_sync")


setuptools.setup(
    name="django-rest-async",
    version=version,
    author="Vsevolod Dudakov",
    author_email="vsdudakov@gmail.com",
    description="Async Django REST framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="BSD",
    url="https://github.com/ukwahlula/django-rest-async",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=["django>=3.1", "pydantic>=1.0"],
    python_requires=">=3.9",
)
