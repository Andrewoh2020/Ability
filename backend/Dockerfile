FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN apt update && apt install -y curl gnupg
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
RUN apt install -y nodejs
RUN npm install -g @anthropic-ai/claude-code

RUN pip install --upgrade pip

COPY pyproject.toml ./
COPY app ./app

RUN pip install --no-cache-dir -e .

RUN apt update && apt install -y iputils-ping


CMD ["uvicorn", "app.main:app", "--host","0.0.0.0","--port","8000"]
