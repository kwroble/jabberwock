from setuptools import setup, find_packages
from dunamai import Version

setup(
    name="jabberwock",
    version=Version.from_any_vcs().serialize(),
    author="Kyle Wroble",
    author_email="kwroble@gmail.com",
    url="https://github.com/kwroble",
    description="Python library that helps with accessing Cisco Call Manager over the AXL interface",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
    ],
    install_requires=["appdirs", "attrs", "boltons", "cached-property", "certifi", "chardet", "defusedxml", "idna",
                      "isodate", "lxml", "pytz", "requests", "requests-toolbelt", "six", "urllib3", "zeep", "dunamai"],
)
