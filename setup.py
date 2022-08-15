""" Setup script for BabyRobotEnv """

# Standard library imports
import pathlib

# Third party imports
from setuptools import find_packages, setup

# The directory containing this file
HERE = pathlib.Path(__file__).resolve().parent

# The text of the README file is used as a description
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="babyrobot",
    version="1.0.2",
    description="An OpenAI Gym Environment for BabyRobot",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/WhatIThinkAbout/BabyRobotGym",
    author="Steve Roberts",
    author_email="steve@steveroberts.name",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    packages = find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=['gym','ipycanvas==0.11']    
)
