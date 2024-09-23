# !/usr/bin/env python
# This file shouldn't have further modifications. All config should be done in setup.cfg.
# setup.py is (slowly) becoming a last resource for complex projects, and setup.cfg is more PEP517 compliant
# The reason this template/project includes this file is to allow `pip install -e .`. The -e (--editable) option
# cannot be called with only a setup.cfg/pyproject.toml configuration.
from distutils.core import setup

setup()
