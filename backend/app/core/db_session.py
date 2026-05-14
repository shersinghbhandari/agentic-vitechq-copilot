from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session

from app.core.database import SessionLocal


@contextmanager
def transactional_session() -> Generator[Session, None, None]:
    """
    Centralized DB transaction boundary.

    Success:
        commit automatically

    Failure:
        rollback automatically

    Always:
        close session
    """
    db: Session = SessionLocal()

    try:
        with db.begin():
            yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()