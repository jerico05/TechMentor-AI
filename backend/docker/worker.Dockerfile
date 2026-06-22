# Worker image: same as backend, but default CMD runs Celery.
# Built from the backend Dockerfile context, override CMD in compose.
FROM techmentor-backend:latest

# Worker doesn't need to expose ports.
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD celery -A app.workers.celery_app inspect ping -d "celery@$HOSTNAME" || exit 1

CMD ["celery", "-A", "app.workers.celery_app", "worker", "--loglevel=info", "--concurrency=2"]
