Welcome to the tox automation project
=====================================

vision: standardize testing in Python
-------------------------------------

``tox`` aims to automate and standardize testing in Python.  It is part
of a larger vision of easing the packaging, testing and release process
of Python software.

What is tox?
------------

tox is a generic virtualenv_ management and test command line tool you can use for:

* checking your package installs correctly with different Python versions and
  interpreters

* running your tests in each of the environments, configuring your test tool of choice

* acting as a frontend to Continuous Integration servers, greatly
  reducing boilerplate and merging CI and shell-based testing.

Why tox3 and not tox?
---------------------
One can notice that most content here is written under the name tox, however the 
projects current name is tox3. Why? tox was started back in 2010, and its code base
has evolved over time with the addition of new features. Also the test suits have become
slower and slower throughout time, and the current maintainers (me included) have had
difficulties to know which one is needed, which one is optional in an effort to speed it
up. What's even more troublesome is that adding new features is not as easy, cause one
always needs to keep in mind backward compatibility.

tox3_ aims to be a rewrite of the original tool, with new requirements, that mostly offers
feature parity with tox, but takes into account how Python evolved in the last 8 years.
Here's a list of new constraints:

- runs under Python ``3.6.0+``, however still allows creation of ``Python 2.7.0`` virtual
  environments (under the hood uses asyncio, so this could lead to better resource usage,
  plus allows to print in parallel stdout/stderr streams).

New features:

- configuration part of ``pyproject.toml``
- PEP 517/518 support (installation of build, and for build requirements - this allows non setuptools 
  workflow, e.g. flint) - this also means that the one can configure the Python (and its virtualenv)
  the tool uses for build
- by default build wheels instead of sdist (but still allow the user to choose sdist)
- better variable substitution in the configs (all string values can be substituted, into a string,
  not just some fields),
- to create the run virtual environment use the new built in ``venv`` module, however for Python 2 fallback
  to the virtualenv package
- by default work directory is under home folder (this is so that IDEs don't try indexing, 
  searching in them, wrongfully believing of the tox work dir to be source folders)
- better dependency management for virtualenvs (so the virtualenv is rebuilt when your dependencies
  change, not just in the config file, but e.g. also when they change in your setup.py). 
- better control over the verbosity of the invocation (e.g. don't hide away wheel/sdist build).

It's not yet production ready, but I would say ready for early adopters. When I can will start
implementing some missing features, and hopefully in a month or two can get a release candidate
with the goal to replace tox. ``tox3`` uses ``tox3`` for itself, to follow the mantra of eat
your own dog food (``PYTHONPATH= python -m tox3 -vvvv`` runs all tests and checks).

.. _virtualenv: https://pypi.python.org/pypi/virtualenv
.. _tox3: https://github.com/gaborbernat/tox3