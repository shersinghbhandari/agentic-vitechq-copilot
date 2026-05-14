from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session

from app.core.database import SessionLocal


@contextmanager
def transactional_session() -> Generator[Session, None, None]:
    """
    Centralized DB transaction/session handler.

    Success:
        commit automatically

    Failure:
        rollback automatically

    Always:
        close session
    """
    db: Session = SessionLocal()

    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()