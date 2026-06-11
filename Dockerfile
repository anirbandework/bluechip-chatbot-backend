# BluChip Agent-Assist — backend container.
# Portable: runs unchanged on Railway, Azure Container Apps, Fly, Render, etc.
# The platform injects $PORT; we bind 0.0.0.0:$PORT.

FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install dependencies first (cached layer). Only pyproject + the package source
# are needed to resolve and install the deps declared in pyproject.toml.
COPY pyproject.toml ./
COPY app ./app
RUN pip install --no-cache-dir .

# Copy the rest of the source (knowledge_sources/, etc.). Kept after the
# dependency install so editing knowledge files doesn't bust the deps layer.
COPY . .

EXPOSE 8000

# Run from source (python -m → cwd on sys.path) so the SOP/knowledge data files
# resolve relative to /app. $PORT is provided by the host; default 8000 locally.
CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
