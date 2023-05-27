# PyTests

![coverage](https://img.shields.io/badge/coverage-98-blueviolet)

This directory is contains files for testing the code. Simply by running `pytest` from
the root directory, all tests will be run with default parameters specified in
`pyproject.toml`. Notable optional parameters include...

- Coverage items. The coverage report indicates what percentage of the code was included
  in tests.
    - `--cov=automation`: Which package should be described in the coverage report
    - `--cov-report term-missing`: Include lines of items missing in coverage
- Verbosity.
    - `-v`: List individual tests, report pass/fail
    - `--my-verbose False`: Default True. Custom verbosity setting to silence typical
    logging. Set to False to see less.
- Saving output files.
    - `--my-teardown True`: Default True. When done with testing, remove created files.
    Set to false to inspect output items after testing.
    - `--my-datadir ./rel-path/`: Default `./tests/test_data/`. Where to store created
      files.
- Incremental running.
    - `--sw`: Stepwise. Continue from previously failed test when starting again.
    - `-s`: No capture. By including `from IPython import embed; embed()` in a test, and
      using this flag, you can open an IPython environment from within a test
    - `--pdb`: Enter debug mode if a test fails.
    - `tests/test_file.py -k test_name`: To run just a set of tests, specify the file
      name at the end of the command. To run a single test, further specify `-k` with
      the test name.

When customizing parameters, comment out the `addopts` line in `pyproject.toml`.

N.B.: `test_export.py:test_split_pdf` takes ~10s. For faster testing, comment this out.
Future versions of this repo will remove this feature.
