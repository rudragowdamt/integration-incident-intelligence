install:
	pip install -r requirements.txt

data:
	python src/data_generator.py --rows 1000

train:
	python src/train.py

evaluate:
	python src/evaluate.py

test:
	pytest -q

api:
	uvicorn src.api:app --reload
