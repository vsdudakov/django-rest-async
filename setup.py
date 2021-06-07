import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-rest-async",
    version="0.0.1",
    author="Vsevolod Dudakov",
    author_email="vsdudakov@gmail.com",
    description="Async Django REST framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ukwahlula/django-rest-async",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.9",
)
