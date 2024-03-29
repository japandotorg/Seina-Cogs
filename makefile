reformat:
	black --target-version py38 -l 99 `git ls-files "*.py" "*.pyi"`
	isort --profile=black `git ls-files "*.py"`
	autoflake -r -i `git ls-files "*.py"`
stylecheck:
	black --check --target-version py38 -l 99 `git ls-files "*.py" "*.pyi"`
	isort --check-only --profile=black `git ls-files "*.py"`