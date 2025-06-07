# LUCA Dev Assistant Makefile

.PHONY: all test lint safety clean docs help

# Default target - run full safety check
all: safety docs

# Run all tests
test:
	@echo "Running tests..."
	LUCA_TESTING=1 pytest -q

# Run all linters
lint:
	@echo "Running linters..."
	black .
	isort .
	flake8 --config=.config/.flake8
	bandit -c .config/pyproject.toml -r luca_core app tools -ll

# Run safety check script
safety:
	@echo "Running safety checks..."
	./scripts/dev-tools/safety-check.sh

# Remove generated files
clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/

# Check documentation is current
docs:
	@echo "Checking documentation..."
	./scripts/dev-tools/verify-docs.sh

# Build Docker image and run tests with CPU/RAM caps
test-docker:
	docker build -f docker/Dockerfile.test -t luca-test .
	docker run --rm --cpus="1" --memory="2g" luca-test

# Help target - display available commands
help:
	@echo "LUCA Dev Assistant Makefile Commands:"
	@echo "  make all        - Run full safety check (default)"
	@echo "  make test       - Run all tests"
	@echo "  make lint       - Run all linters (black, isort, flake8, bandit)"
	@echo "  make safety     - Run safety-check.sh script"
	@echo "  make clean      - Remove generated files and caches"
	@echo "  make docs       - Check documentation is current"
	@echo "  make test-docker - Build and run tests in Docker container"
	@echo "  make help       - Display this help message"