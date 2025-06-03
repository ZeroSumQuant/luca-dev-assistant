# -------- Luca base image --------
FROM python:3.13-slim

# Set a working directory inside the container
WORKDIR /app

# Copy only dependency list first for layer caching
COPY requirements.txt .

# Install dependencies without cache to keep the image small
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the source
COPY . .

# Default command: run the bootstrap banner
CMD ["python", "scripts/start_assistant.py"]
