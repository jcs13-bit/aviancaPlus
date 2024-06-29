FROM python:3.9-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir werkzeug==2.0.2  # Asegúrate de especificar la versión correcta de Werkzeug

CMD ["python", "app.py"]
