from setuptools import setup, find_packages

setup(
    name="jabberwock",
    version="0.6.2",
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
                      "isodate", "lxml", "pytz", "requests", "requests-toolbelt", "six", "urllib3", "zeep"],
)
