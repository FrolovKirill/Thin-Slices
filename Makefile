.PHONY: install run clean

install:
	python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

run:
	. venv/bin/activate && python manage.py runserver 0.0.0.0:8000

migrate:
	. venv/bin/activate && python manage.py migrate

clean:
	rm -rf venv
	find . -name "__pycache__" -exec rm -rf {} +