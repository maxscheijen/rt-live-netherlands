lint:
	black .
	flake8 --ignore E501,E722  src/
	flake8 --ignore E501,E722 tests/

.PHONY: data
data:
	python3 src/data.py

test:
	python3 -m pytest tests/

run:
	python3 -m src.run