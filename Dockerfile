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
COPY dependencies/ dependencies/
RUN poetry lock

COPY stargazefloorbot/ stargazefloorbot/
RUN poetry install --no-dev

ENTRYPOINT [ "python", "-m", "stargazefloorbot" ]
