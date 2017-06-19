#!/bin/bash
celery worker -A slack.celery &
gunicorn slack:app