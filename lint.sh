#!/usr/bin/env bash

poetry run isort stargazefloorbot
poetry run black stargazefloorbot
poetry run flake8 stargazefloorbot
