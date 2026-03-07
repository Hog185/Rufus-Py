# How to run tests
1. Activate `.venv` and install `pytest`, plus any other required dependencies for the project.
2. With the correct interpreter, run the tests:

```sh
python -m pytest -q
```

If your virtual environment is not activated, run:

```sh
/home/kero/Documents/Projects/lufus-Dev/.venv/bin/python -m pytest -q
```

To run a single test file:

```sh
python -m pytest tests/test_check_file_sig.py -q
```

3. The output will show which tests passed and failed.
4. Update tests as needed, but never intentionally make a test fail.

# How to make your own tests

1. Create a new file in the `tests/` directory with a name that starts with `test_` and ends with `.py` (for example, `test_my_feature.py`).
2. Import the necessary modules and write test functions that start with `test_` (for example, `test_my_feature_functionality`).
3. Use assertions to compare expected and actual outcomes (for example, `assert my_function() == expected_result`).
4. Save the file and run the tests using the command above.

# Important Notes

- Write meaningful test cases that cover different scenarios for the function(s) you are testing.
- If you need to change an existing test, explain the change and reason explicitly in your PR. Changes (NOT ADDITIONAL TESTS) to already-defined test files without proper reasoning may be immediately rejected.
- If your PR is rejected for missing reasoning, no worries. resubmit with a clear explanation.
- If you add a new feature, add tests for it. If the function is in a new source file, create a matching test file in `tests/`. If the function is in an existing source file, add tests to the corresponding existing test file. Example: if you add a function in `check_file_sig.py`, add its tests in `test_check_file_sig.py`.
- Have questions? DM me on Discord (`_kerr0`) or open an issue in the repo. For contributors, please forward test-related issues to me. I made these tests, so I likely know them best and I’m happy to help ^^