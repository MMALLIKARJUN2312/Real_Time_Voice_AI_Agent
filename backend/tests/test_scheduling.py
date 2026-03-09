import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base
from services.scheduling import check_availability, book_appointment

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()

def test_check_availability_empty(db_session):
    slots = check_availability(db_session, "dr_test", "2026-03-20")
    assert isinstance(slots, list)
