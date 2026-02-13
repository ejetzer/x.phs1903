# Tests automatisés
dir_tests = tests

test_twine: python
	$(twine) upload -r testpypi $(python_build)/* $(python_wheel)/*