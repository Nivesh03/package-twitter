import os
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import tweepy

from src.package_twitter.tweet import TwitterBot


# Mock environment variables for testing
@pytest.fixture(autouse=True)
def mock_env_vars():
    with patch.dict(
        os.environ,
        {
            "TWITTER_CONSUMER_KEY": "mock_consumer_key",
            "TWITTER_CONSUMER_SECRET": "mock_consumer_secret",
            "TWITTER_ACCESS_TOKEN": "mock_access_token",
            "TWITTER_ACCESS_TOKEN_SECRET": "mock_access_token_secret",
        },
    ):
        yield


def test_twitter_bot_initialization():
    bot = TwitterBot()
    assert bot.consumer_key == "mock_consumer_key"
    assert isinstance(bot.client, tweepy.Client)


def test_twitter_bot_initialization_missing_env():
    # Test case where a specific env var is missing
    with patch.dict(os.environ, {"TWITTER_CONSUMER_KEY": ""}, clear=True):
        with pytest.raises(ValueError, match="Twitter API credentials not found"):
            TwitterBot()


@patch("tweepy.Client.create_tweet")
def test_post_tweet_success(mock_create_tweet):
    mock_create_tweet.return_value = MagicMock(
        data={"id": "12345", "text": "Hello, Twitter!"}
    )
    bot = TwitterBot()
    tweet_text = "Hello, Twitter!"
    response_data = bot.post_tweet(tweet_text)
    mock_create_tweet.assert_called_once_with(text=tweet_text)
    assert response_data["id"] == "12345"
    assert response_data["text"] == "Hello, Twitter!"


def test_post_tweet_empty_text():
    bot = TwitterBot()
    with pytest.raises(ValueError, match="Tweet text cannot be empty."):
        bot.post_tweet("")


def test_post_tweet_long_text():
    bot = TwitterBot()
    long_text = "a" * 281
    with pytest.raises(ValueError, match="Tweet text exceeds 280 characters."):
        bot.post_tweet(long_text)


@patch("tweepy.Client.create_tweet")
def test_post_tweet_api_error(mock_create_tweet):
    mock_create_tweet.side_effect = tweepy.TweepyException(
        "API Error 401: Unauthorized"
    )
    bot = TwitterBot()
    with pytest.raises(tweepy.TweepyException, match="API Error 401: Unauthorized"):
        bot.post_tweet("This tweet will fail.")
