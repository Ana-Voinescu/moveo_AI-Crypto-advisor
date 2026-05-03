import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from app.database import Base
from app.models.user import User
from app.models.preferences import UserPreferences
from app.models.content_vote import ContentVote


# --- Fixtures ---

@pytest.fixture(scope="function")
def db():
    """
    Each test gets a fresh in-memory SQLite DB.
    Tables are created before the test and dropped after.
    """
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


def make_user(name="Alice", email="alice@example.com"):
    return User(name=name, email=email, password_hash="hashed_pw")


# --- User tests ---

def test_create_user(db):
    user = make_user()
    db.add(user)
    db.commit()

    result = db.query(User).filter_by(email="alice@example.com").first()
    assert result is not None
    assert result.name == "Alice"
    assert result.is_onboarded is False
    assert result.created_at is not None


def test_duplicate_email_raises(db):
    db.add(make_user())
    db.commit()

    db.add(make_user())  # same email
    with pytest.raises(IntegrityError):
        db.commit()


# --- UserPreferences tests ---

def test_create_preferences(db):
    user = make_user()
    db.add(user)
    db.commit()

    prefs = UserPreferences(
        user_id=user.id,
        crypto_assets=["BTC", "ETH"],
        investor_type="hodler",
        content_types=["news", "fun"],
    )
    db.add(prefs)
    db.commit()

    result = db.query(UserPreferences).filter_by(user_id=user.id).first()
    assert result is not None
    assert result.crypto_assets == ["BTC", "ETH"]
    assert result.investor_type == "hodler"
    assert result.content_types == ["news", "fun"]


def test_one_preference_per_user(db):
    user = make_user()
    db.add(user)
    db.commit()

    db.add(UserPreferences(user_id=user.id, crypto_assets=["BTC"], investor_type="hodler", content_types=["news"]))
    db.commit()

    db.add(UserPreferences(user_id=user.id, crypto_assets=["ETH"], investor_type="day_trader", content_types=["charts"]))
    with pytest.raises(IntegrityError):
        db.commit()


# --- ContentVote tests ---

def test_create_vote(db):
    user = make_user()
    db.add(user)
    db.commit()

    vote = ContentVote(user_id=user.id, content_type="news", content_id="article-123", vote=True)
    db.add(vote)
    db.commit()

    result = db.query(ContentVote).filter_by(user_id=user.id, content_id="article-123").first()
    assert result is not None
    assert result.vote is True


def test_upsert_vote(db):
    """Changing a vote updates the existing row instead of inserting a duplicate."""
    user = make_user()
    db.add(user)
    db.commit()

    # First vote: thumbs up
    vote = ContentVote(user_id=user.id, content_type="news", content_id="article-123", vote=True)
    db.add(vote)
    db.commit()

    # Change to thumbs down
    existing = db.query(ContentVote).filter_by(
        user_id=user.id, content_type="news", content_id="article-123"
    ).first()
    existing.vote = False
    existing.updated_at = datetime.utcnow()
    db.commit()

    all_votes = db.query(ContentVote).filter_by(user_id=user.id, content_id="article-123").all()
    assert len(all_votes) == 1          # still one row, not two
    assert all_votes[0].vote is False   # vote was updated


def test_duplicate_vote_raises(db):
    """Inserting two separate rows for the same (user, content_type, content_id) must fail."""
    user = make_user()
    db.add(user)
    db.commit()

    db.add(ContentVote(user_id=user.id, content_type="meme", content_id="meme-1", vote=True))
    db.commit()

    db.add(ContentVote(user_id=user.id, content_type="meme", content_id="meme-1", vote=False))
    with pytest.raises(IntegrityError):
        db.commit()
