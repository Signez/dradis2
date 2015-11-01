from dradis.main import app, celery
from dradis.common import tasks

# Run me like this:
# celery -A dradis.main.celery worker --autoreload -l INFO

