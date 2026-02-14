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

spam-check:
	@for i in 1 2 3 4 5 6 7; do \
		echo "Request $$i:"; \
		curl -s -X POST http://localhost:8080/check -H "Content-Type: application/json" -d '{"key": "user1", "limit": 5, "window_seconds": 10}'; \
		echo ""; \
	done


.PHONY: test
test:
	.venv/bin/pytest test/