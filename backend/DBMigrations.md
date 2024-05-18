# Step-by-step documentation for database migrations with alembic

From `backend` directory.

## Creating migration
```console
alembic revision --autogenerate -m "migration message"
```

## Applying the migration
```console
alembic upgrade head
```