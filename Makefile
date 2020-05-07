help:
	@echo "make"
	@echo "    clean"
	@echo "        Remove Python/build artifacts."
	@echo "    formatter"
	@echo "        Apply black formatting to code."
	@echo "    lint"
	@echo "        Lint code with flake8, and check if black formatter should be applied."
	@echo "    types"
	@echo "        Check for type errors using pytype."
	@echo "    validate"
	@echo "        Runs the rasa data validate to verify data."
	@echo "    test"
	@echo "        Runs the rasa test suite checking for issues."
	@echo "    crossval"
	@echo "        Runs the rasa cross validation tests and creates results.md"
	@echo "    shell"
	@echo "        Runs the rasa train and rasa shell for testing"


clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f  {} +
	rm -rf build/
	rm -rf .pytype/
	rm -rf dist/
	rm -rf docs/_build

formatter:
	black actions --line-length 79

lint:
	flake8 actions.py
	black --check actions --line-length 79

types:
	pytype --keep-going actions

validate:
	rasa train
	rasa data validate --debug

test:
	rasa train
	rasa test --fail-on-prediction-errors

crossval:
	rasa test nlu -f 5 --cross-validation
	python format_results.py

shell:
	rasa train --debug
	rasa shell --debug