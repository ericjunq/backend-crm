import pytest 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from main import app 
from fastapi.testclient import TestClient
from dependencies import get_db
from settings import settings

engine = create_engine(
    settings.database_url_test,
    connect_args={'check_same_thread': False}
)

TestingLocalSession = sessionmaker(
    autocommit = False,
    autoflush=False,
    bind=engine
)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingLocalSession()
    try: 
        yield session
    finally:
        session.close()

@pytest.fixture()
def cliente(db):
    def override_get_db():
        try:
            yield db 
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()