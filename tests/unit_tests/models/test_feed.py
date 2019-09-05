from pytest import fixture

from .conftest import as_dicts
from ..conftest import random_int


class TestFeed:

    @fixture
    def mock_likers(self, mocker, users):
        return mocker.patch(
            'instapi.client.client.media_likers',
            return_value={'users': as_dicts(users)},
        )

    @fixture
    def mock_comments(self, mocker, comments):
        return mocker.patch(
            'instapi.client.client.media_comments',
            return_value={'comments': as_dicts(comments)},
        )

    @fixture
    def mock_timeline(self, mocker, feeds):
        return mocker.patch(
            'instapi.client.client.feed_timeline',
            return_value={'feed_items': [{'media_or_ad': f.as_dict()} for f in feeds]},
        )

    @fixture
    def mock_images(self, mocker, images):
        return mocker.patch(
            'instapi.models.base.Media._media_info',
            return_value=images[0].as_dict(),
        )

    @fixture
    def mock_videos(self, mocker, videos):
        return mocker.patch(
            'instapi.models.base.Media._media_info',
            return_value=videos[0].as_dict(),
        )

    def test_like(self, mocker, feed):
        like_mock = mocker.patch('instapi.client.client.post_like')

        feed.like()

        like_mock.assert_called_once_with(feed.pk)

    def test_unlike(self, mocker, feed):
        unlike_mock = mocker.patch('instapi.client.client.delete_like')

        feed.unlike()

        unlike_mock.assert_called_once_with(feed.pk)

    def test_liked_by_user_in_likers(self, mock_likers, feed, users):
        user, *_ = users

        assert feed.liked_by(user)

    def test_liked_by_user_not_in_likers(self, mock_likers, feed, users, user):
        assert not feed.liked_by(user)

    def test_iter_likes(self, mock_likers, feed, users):
        unpack = [*feed.iter_likes()]

        assert unpack == users

    def test_likes_without_limit(self, mock_likers, feed, users):
        likes = feed.likes()

        assert likes == users

    def test_likes_with_limit(self, mock_likers, feed, users):
        limit = random_int(0, len(users))
        likes = feed.likes(limit=limit)

        assert likes == users[:limit]

    def test_iter_comments(self, mock_comments, feed, comments):
        unpack = [*feed.iter_comments()]

        assert unpack == comments

    def test_comments_without_limit(self, mock_comments, feed, comments):
        assert feed.comments() == comments

    def test_comments_with_limit(self, mock_comments, feed, comments):
        limit = random_int(0, len(comments))

        assert feed.comments(limit=limit) == comments[:limit]

    def test_iter_timeline(self, mock_timeline, feed, feeds):
        assert [*feed.iter_timeline()] == feeds

    def test_timeline_without_limit(self, mock_timeline, feed, feeds):
        assert feed.timeline() == feeds

    def test_timeline_with_limit(self, mock_timeline, feed, feeds):
        limit = random_int(0, len(feeds))
        feeds = feed.timeline(limit=limit)

        assert feeds == feeds[:limit]

    def test_iter_resources_videos_without_carusel(self, mock_videos, videos, feed):
        assert [*feed.iter_resources()] == videos

    def test_iter_resources_images_without_carusel(self, mock_images, images, feed):
        assert [*feed.iter_resources()] == images

    def test_resources_videos(self, mock_videos, videos, feed):
        assert feed.resources() == videos

    def test_resources_images(self, mock_images, images, feed):
        assert feed.resources() == images

    def test_iter_videos(self, mock_videos, videos, feed):
        assert [*feed.iter_videos()] == videos

    def test_videos(self, mock_videos, videos, feed):
        assert feed.videos() == videos

    def test_iter_images(self, mock_images, images, feed):
        assert [*feed.iter_images()] == images

    def test_images(self, mock_images, images, feed):
        assert feed.images() == images

    def test_video(self, mock_videos, videos, feed):
        assert feed.video() == videos[0]

    def test_image(self, mock_images, images, feed):
        assert feed.image() == images[0]