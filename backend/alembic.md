# Alembic Database Migrations Guide

Alembic is a database migration tool for SQLAlchemy. It helps you track and apply changes to your database schema over time.

## The Workflow

### 1. Add/Change columns in your model

Edit `models.py` to add new columns:

```python
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # NEW COLUMNS YOU WANT TO ADD
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
```

### 2. Generate migration automatically

```bash
.venv/bin/alembic revision --autogenerate -m "Add user name fields"
```

This compares your models to the actual database and creates a migration file.

### 3. Review the migration

Check the generated file in `alembic/versions/`. Make sure it does what you want.

### 4. Apply the migration

```bash
.venv/bin/alembic upgrade head
```

This runs the migration and updates your database.

---

## Common Commands

```bash
# Check current migration status
.venv/bin/alembic current

# See migration history
.venv/bin/alembic history

# Rollback one migration
.venv/bin/alembic downgrade -1

# Rollback to specific revision
.venv/bin/alembic downgrade <revision_id>

# Upgrade to latest
.venv/bin/alembic upgrade head
```

---

## Important Notes

- **Always review** the generated migration before applying it
- Alembic compares your SQLAlchemy models to the actual database schema
- The `upgrade()` function applies changes, `downgrade()` reverts them
- You can use any password length with argon2 (no 72-byte bcrypt limitation)
- Migrations are stored in `alembic/versions/`

---

## Example: Adding Columns

1. Edit `models.py` and add your new columns
2. Run: `.venv/bin/alembic revision --autogenerate -m "descriptive message"`
3. Review the generated file in `alembic/versions/`
4. Run: `.venv/bin/alembic upgrade head`
5. Done! Your database now has the new columns
