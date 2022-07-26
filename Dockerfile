###
FROM python:3.10 as poetry_builder

ENV PATH="/root/.local/bin:$PATH"
ENV POETRY_VIRTUALENVS_CREATE=false

RUN curl -sSL https://install.python-poetry.org | python -

###
FROM poetry_builder as builder

WORKDIR /stargaze-floor-bot
COPY cache/ cache/
COPY pyproject.toml .
COPY poetry.lock .
COPY dependencies/ dependencies/
RUN poetry install --no-dev --no-root

COPY stargazefloorbot/ stargazefloorbot/
RUN poetry install --no-dev

ENV INTERVAL=300
ENV CONFIG_FILE=/stargaze-floor-bot/config.json

ENTRYPOINT [ "python", "-m", "stargazefloorbot" ]
