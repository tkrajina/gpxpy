# Contributing to gpxpy

gpxpy aims to be a full featured library for handling gpx files defined by the GPX 1.0 and 1.1 schemas. Specifically, it should:

- Be able to lossless read any well-formed and valid gpx (1.0 or 1.1)
- Be able to manipulate all gpx fields defined by the schema
- Provide convenience functions for common computations and manipulations
- Be able to lossless write out any well-formed and valid gpx


Bug fixes, feature additions, tests, documentation and more can be contributed via [issues](https://github.com/tkrajina/gpxpy/issues) and/or [pull requests](https://github.com/tkrajina/gpxpy/pulls). All contributions are welcome.

## Bug fixes, feature additions, etc.

Please send a pull requests for new features or bugfixes to the `dev` branch. Minor changes or urgent hotfixes can be sent to `master`.
Please include tests for new features. Tests or documentation without bug fixes or feature additions are welcome too. Feel free to ask any questions [via issues](https://github.com/tkrajina/gpxpy/issues/new).

- Fork the gpxpy repository.
- Create a branch from master.
- Develop bug fixes, features, tests, etc.
- Run the test suite on both Python 2.x and 3.x. You can enable [Travis CI](https://travis-ci.org/profile/) on your repo to catch test failures prior to the pull request, and [Coveralls](https://coveralls.io) to see if the changed code is covered by tests.
- Create a pull request to pull the changes from your branch to the gpxpy master.

If you plan a big refactory, open an issue for discussion before starting it.

### Guidelines

Library code is read far more than it is written. Keep your code clean and understandable.
- Provide tests for any newly added code.
- Follow PEP8 and use pycodestyle for new code.
- Follow PEP257 and use pydocstyle. Additionally, docstrings should be styled like Google's [Python Style Guide](https://google.github.io/styleguide/pyguide.html?showone=Comments#Comments)
- New code should pass flake8
- Avoid decreases in coverage

## Reporting Issues

When reporting issues, please include code that reproduces the issue and whenever possible, a gpx that demonstrates the issue. The best reproductions are self-contained scripts with minimal dependencies.

### Provide details

- What did you do?
- What did you expect to happen?
- What actually happened?
- What versions of gpxpy, lxml and Python were you using?
