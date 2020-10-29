FROM rasa/rasa-sdk:2.0.0

WORKDIR /app

COPY actions /app/actions

USER root

RUN pip install --no-cache-dir -r actions/requirements-actions.txt

USER 1001

CMD ["start", "--actions", "actions", "--debug"]
