FROM rasa/rasa-sdk:1.10.0

WORKDIR /app

COPY requirements-actions.txt ./

USER root

RUN pip install --no-cache-dir -r requirements-actions.txt

COPY ./actions.py ./__init__.py ./snow_credentials.yml ./

RUN pip install .

USER 1001

CMD ["start", "--actions", "actions", "--debug"]