from setuptools import setup
import toml

PYPROJECT_DATA = toml.load('pyproject.toml')
NAME = PYPROJECT_DATA['tool']['poetry']['name']
VERSION = PYPROJECT_DATA['tool']['poetry']['version']

setup(name=NAME, version=VERSION)
