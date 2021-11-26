from setuptools import setup, find_packages
from dunamai import Version
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.rst").read_text()

setup(
    name="jabberwock",
    version=Version.from_any_vcs().base,
    author="Kyle Wroble",
    author_email="kwroble@gmail.com",
    url="https://github.com/kwroble/jabberwock",
    description="Python library that helps with accessing Cisco Call Manager over the AXL interface",
    long_description=long_description,
    long_description_content_type='text/x-rst',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
    ],
    install_requires=["appdirs", "attrs", "boltons", "cached-property", "certifi", "chardet", "defusedxml", "idna",
                      "isodate", "lxml", "pytz", "requests", "requests-toolbelt", "six", "urllib3", "zeep", "dunamai"],
)
