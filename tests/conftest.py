import pytest
from flood_app import create_app
from flood_app.db import db as _db
from flood_app.models import AppMetadata, Shelter


class TestConfig:
    SECRET_KEY = "test-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_DEBUG = True
    TEMPLATE_DIR = "templates"
    STATIC_DIR = "static"


@pytest.fixture
def app():
    app = create_app(TestConfig)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()


@pytest.fixture
def seed_data(db):
    shelter = Shelter(
        name="Test Shelter",
        capacity=100,
        available_beds=50,
        distance=5.0,
        accessibility="easy",
        elevation_level="high",
        proximity_to_water="far",
        medical_facility="advanced",
        latitude=20.0,
        longitude=85.0
    )
    db.session.add(shelter)
    db.session.add(AppMetadata(key="source_type", value="test"))
    db.session.commit()
    return shelter
