import codecs
import os
from platform import python_version

from setuptools import find_packages, setup

PACKAGE_NAME = "syntax-coloring"
VERSION = "0.1"
AUTHOR = "Igor Majic"
AUTHOR_EMAIL = "majic753@gmail.com"
DESCRIPTION = "A syntax highlighting generator for any language"
KEYWORDS = "textX DSL python all languages highlighting coloring"
LICENSE = "MIT"
URL = "https://github.com/IgorMaj/SyntaxColoring"

packages = find_packages()

print("packages:", packages)

# README = codecs.open(
#    os.path.join(os.path.dirname(__file__), "README.md"), "r", encoding="utf-8"
# ).read()


setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    # long_description=README,
    long_description_content_type="text/markdown",
    url=URL,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    keywords=KEYWORDS,
    license=LICENSE,
    packages=packages,
    include_package_data=True,
    install_requires=["click", "jinja2", "textx"],
    entry_points={
        "textx_generators": ["gen_coloring = gen_coloring:textmate_gen_coloring"]
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
