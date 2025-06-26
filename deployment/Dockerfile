FROM python:3.10-slim
WORKDIR /app
COPY deployment/setup.py deployment/requirements.txt ./
COPY src/ ./src/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -e .
EXPOSE 5000