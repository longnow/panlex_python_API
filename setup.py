from setuptools import setup, find_packages

setup(
    name='panlex_API',
    version='1.0.0',
    author="Maxwell Joslyn; Caroline Glazer"
    author_email="",
    url="panlex.org",
    description='Python wrapper for PanLex API',
    install_requires=['ratelimit','requests'],
    classifiers=["Development Status :: 5 - Production/Stable", "Programming Language :: Python",
                 "Programming Language :: Python :: 3", "Operating System :: OS Independent",
                 "License :: OSI Approved :: MIT License", "Topic :: Software Development :: Libraries :: Python Modules"]
)
