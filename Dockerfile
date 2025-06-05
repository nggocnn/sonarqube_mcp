FROM python:3.12-slim
RUN pip install --upgrade uv

WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt

CMD ["python", "src/__main__.py"]