FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .
COPY src src
COPY examples examples
COPY web web
COPY backend_server.py .
RUN pip install --no-cache-dir .
RUN useradd --uid 10001 --create-home appuser
USER appuser
EXPOSE 8080
CMD ["python","-m","http.server","8080","--directory","web"]
