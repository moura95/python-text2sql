include .env
run:
	streamlit run src/main.py
dep:
	pip install -r requirements.txt

.PHONY: run dep
