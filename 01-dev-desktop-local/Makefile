VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
FLAKE8 = $(VENV)/bin/flake8
PYTEST = $(VENV)/bin/pytest

.PHONY: venv install lint test run docker-build docker-run clean

venv:
	python3 -m venv $(VENV)

install: venv
	. $(VENV)/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

lint:
	. $(VENV)/bin/activate && flake8 app.py test_app.py

test:
	. $(VENV)/bin/activate && pytest

run:
	. $(VENV)/bin/activate && python app.py

docker-build:
	docker build -t meuapp:dev .

docker-run:
	docker run --rm -it meuapp:dev

clean:
	rm -rf $(VENV) __pycache__ .pytest_cache
