FROM python:3.13-slim

# Install uv by copying it from the official uv image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy your application code into the container
COPY . /app

WORKDIR /app

# Install dependencies using uv
RUN uv sync --frozen --no-cache

# Run the app using uv's managed environment
CMD ["/app/.venv/bin/python", "main.py"]
