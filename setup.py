import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="breathless-rzlim08", # Replace with your own username
    version="0.0.1",
    author="Ryan Lim",
    description="A package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    python_requires='>=3.5',
)
