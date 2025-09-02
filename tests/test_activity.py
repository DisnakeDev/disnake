# SPDX-License-Identifier: MIT

from typing import TYPE_CHECKING

import pytest

from disnake import activity as _activity

if TYPE_CHECKING:
    from disnake.types.activity import ActivityAssets


@pytest.fixture
def activity():
    return _activity.Activity()


@pytest.fixture
def game():
    return _activity.Game(name="Celeste")


@pytest.fixture
def custom_activity():
    return _activity.CustomActivity(name="custom")


@pytest.fixture
def streaming():
    return _activity.Streaming(name="me", url="https://disnake.dev")


@pytest.fixture
def spotify():
    return _activity.Spotify()


@pytest.fixture(params=["activity", "game", "custom_activity", "streaming", "spotify"])
def any_activity(request):
    return request.getfixturevalue(request.param)


class TestAssets:
    def test_none(self, any_activity: _activity.ActivityTypes) -> None:
        assert any_activity.large_image_url is None
        assert any_activity.small_image_url is None
        assert any_activity.large_image_text is None
        assert any_activity.small_image_text is None

    def test_text(self, any_activity: _activity.ActivityTypes) -> None:
        assets: ActivityAssets = {"large_text": "hi", "small_text": "hello"}
        any_activity.assets = assets

        assert any_activity.large_image_url is None
        assert any_activity.small_image_url is None
        assert any_activity.large_image_text == "hi"
        assert any_activity.small_image_text == "hello"

    def test_mp(self, any_activity: _activity.ActivityTypes) -> None:
        assets: ActivityAssets = {
            "large_image": "mp:external/stuff/large",
            "small_image": "mp:external/stuff/small",
        }
        any_activity.assets = assets

        assert any_activity.large_image_url == "https://media.discordapp.net/external/stuff/large"
        assert any_activity.small_image_url == "https://media.discordapp.net/external/stuff/small"

    def test_unknown_prefix(self, any_activity: _activity.ActivityTypes) -> None:
        assets: ActivityAssets = {"large_image": "unknown:a", "small_image": "unknown:b"}
        any_activity.assets = assets

        assert any_activity.large_image_url is None
        assert any_activity.small_image_url is None

    def test_asset_id(self, any_activity: _activity.ActivityTypes) -> None:
        assets: ActivityAssets = {"large_image": "1234", "small_image": "5678"}
        any_activity.assets = assets

        assert any_activity.large_image_url is None
        assert any_activity.small_image_url is None

    # test `Activity` with application_id separately;
    # without application_id, it should behave like the other types (see previous test)
    def test_asset_id_activity(self, activity: _activity.Activity) -> None:
        activity.application_id = 1010

        assets: ActivityAssets = {"large_image": "1234", "small_image": "5678"}
        activity.assets = assets
        assert activity.large_image_url == "https://cdn.discordapp.com/app-assets/1010/1234.png"
        assert activity.small_image_url == "https://cdn.discordapp.com/app-assets/1010/5678.png"

        # if it's a prefixed asset, it's should return `None` again
        assets: ActivityAssets = {"large_image": "unknown:1234", "small_image": "unknown:5678"}
        activity.assets = assets
        assert activity.large_image_url is None
        assert activity.small_image_url is None
