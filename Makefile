# Run host-side tests
test:
	pytest -q

# Build slim image and run tests with CPU/RAM caps
test-docker:
	docker build -f docker/Dockerfile.test -t luca-test .
	docker run --rm --cpus="1" --memory="2g" luca-test