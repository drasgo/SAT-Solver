try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="SAT",
    version="1.0.0",
    author="Drasgo",
    author_email="tommasocastiglione@gmail.com",
    license="",
    description="SAT solver",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/drasgo/SAT-Solver",
    packages=["SAT"],
    install_requires=[],
    extras_require={},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: CC BY-NC 4.0",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
