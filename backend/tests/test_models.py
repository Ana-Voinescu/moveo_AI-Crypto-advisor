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


# --- Extended DB interaction tests ---

def test_update_preferences_persists_changes(db):
    """Updating existing preferences overwrites old values correctly."""
    user = make_user()
    db.add(user)
    db.commit()

    prefs = UserPreferences(
        user_id=user.id, crypto_assets=["BTC"],
        investor_type="hodler", content_types=["news"],
    )
    db.add(prefs)
    db.commit()

    prefs.crypto_assets = ["ETH", "SOL"]
    prefs.investor_type = "day_trader"
    db.commit()
    db.refresh(prefs)

    assert prefs.crypto_assets == ["ETH", "SOL"]
    assert prefs.investor_type == "day_trader"


def test_is_onboarded_flag_starts_false_and_can_be_set(db):
    """is_onboarded defaults to False and can be flipped to True."""
    user = make_user()
    db.add(user)
    db.commit()

    assert user.is_onboarded is False

    user.is_onboarded = True
    db.commit()
    db.refresh(user)

    assert user.is_onboarded is True


def test_vote_value_changes_after_update(db):
    """Updating a vote's boolean value is reflected after commit and refresh."""
    user = make_user()
    db.add(user)
    db.commit()

    vote = ContentVote(user_id=user.id, content_type="news", content_id="a1", vote=True)
    db.add(vote)
    db.commit()

    vote.vote = False
    db.commit()
    db.refresh(vote)

    assert vote.vote is False


def test_user_can_vote_on_multiple_content_types(db):
    """One user can have one vote per content type without constraint violations."""
    user = make_user()
    db.add(user)
    db.commit()

    for content_type in ["news", "price", "ai_insight", "meme"]:
        db.add(ContentVote(
            user_id=user.id, content_type=content_type, content_id="item-1", vote=True,
        ))
    db.commit()

    votes = db.query(ContentVote).filter_by(user_id=user.id).all()
    assert len(votes) == 4
    assert {v.content_type for v in votes} == {"news", "price", "ai_insight", "meme"}


def test_preferences_linked_to_correct_user(db):
    """user_id FK correctly links preferences back to the user."""
    user = make_user()
    db.add(user)
    db.commit()

    prefs = UserPreferences(
        user_id=user.id, crypto_assets=["BTC"],
        investor_type="hodler", content_types=["fun"],
    )
    db.add(prefs)
    db.commit()

    fetched = db.query(UserPreferences).filter_by(user_id=user.id).first()
    assert fetched is not None
    assert fetched.user.email == "alice@example.com"
