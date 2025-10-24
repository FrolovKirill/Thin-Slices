.PHONY: server install migrate run clean superuser

server: install migrate run

install:
	python3.13 -m venv venv
	. venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

migrate:
	. venv/bin/activate && python3 manage.py migrate

run:
	. venv/bin/activate && python3 manage.py runserver 127.0.0.1:8000

superuser:
	. venv/bin/activate && python3 manage.py createsuperuser

clean:
	rm -rf venv
	find . -name "__pycache__" -exec rm -rf {} +