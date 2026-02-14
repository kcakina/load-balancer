venv:
	python3 -m venv .venv

activate:
	source .venv/bin/activate

install:
	.venv/bin/pip install -r requirements.txt

run:
	.venv/bin/python main.py

test-endpoint:
	curl http://localhost:8080/

test-check:
	curl -X POST http://localhost:8080/check -H "Content-Type: application/json" -d '{"key": "user1", "limit": 5, "window_seconds": 10}'


.PHONY: test
test:
	.venv/bin/pytest test/