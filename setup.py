""" Setup script for BabyRobotEnv """

# Standard library imports
import pathlib
from os.path import join

from jupyter_packaging import get_version

# Third party imports
from setuptools import find_packages, setup

# The directory containing this file
HERE = pathlib.Path(__file__).resolve().parent

# The text of the README file is used as a description
README = (HERE / "README.md").read_text()

# The name of the project
PROJECT = 'babyrobot'

# Get our version
VERSION = get_version(join(PROJECT, '_version.py'))

# This call to setup() does all the work
setup(
    name=PROJECT,
    version=VERSION,
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
    install_requires=['gym==0.25.2','ipycanvas==0.11']    
)
