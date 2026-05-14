from typing import Generator

from sqlalchemy.orm import Session

from app.core.transaction_manager import transactional_session


def get_db() -> Generator[Session, None, None]:
    with transactional_session() as db:
        yield db