from datetime import datetime, timezone
from dateutil import parser as date_parse
import time
import pytest

from truthbrush.api import Api


@pytest.fixture(scope="module")
def api():
    return Api()

def as_datetime(date_str):
    """Datetime formatter function. Ensures timezone is UTC. Consider moving to Api class."""
    return date_parse.parse(date_str).replace(tzinfo=timezone.utc)

# def test_lookup(api):
#     user = api.lookup(user_handle="realDonaldTrump")
#     assert list(user.keys()) == [
#         'id',
#          'serializer',
#          'username',
#          'acct',
#          'display_name',
#          'locked',
#          'bot',
#          'discoverable',
#          'group',
#          'created_at',
#          'note',
#          'url',
#          'avatar',
#          'avatar_static',
#          'header',
#          'header_static',
#          'followers_count',
#          'following_count',
#          'statuses_count',
#          'last_status_at',
#          'verified',
#          'location',
#          'website',
#          'accepting_messages',
#          'chats_onboarded',
#          'feeds_onboarded',
#          'tv_onboarded',
#          'bookmarks_onboarded',
#          'show_nonmember_group_statuses',
#          'pleroma',
#          'tv_account',
#          'receive_only_follow_mentions',
#          'group_reactions_onboarded',
#          'premium',
#          'emojis',
#          'fields'
#             ]
#     assert isinstance(user["id"], str)

def test_pull_statuses(api):
    username = "realDonaldTrump"
    # COMPLETE PULLS
    # it fetches a timeline of the user's posts:
    while(True):
        latest_post="114698009192914684"
        full_timeline = list(
            api.pull_statuses(username=username, replies=False, verbose=True, since_id=latest_post)
        )
        #assert len(full_timeline) > 0  # more than one page

        # the posts are in reverse chronological order:
        latest, earliest = full_timeline[0], full_timeline[-1]
        latest_at, earliest_at = as_datetime(latest["created_at"]), as_datetime(
            earliest["created_at"]
        )
        assert earliest_at < latest_at

        # EMPTY PULLS

        # can use created_after param for filtering out posts:
        next_pull = list(
            api.pull_statuses(
                username=username, replies=False, created_after=latest_at, verbose=True
            )
        )
        assert not any(next_pull)

        # can use since_id param for filtering out posts:
        next_pull = list(
            api.pull_statuses(
                username=username, replies=False, since_id=latest["id"], verbose=True
            )
        )
        assert not any(next_pull)

        # PARTIAL PULLS

        n_posts = 1  # two and a half pages worth, to verify everything is ok
        recent = full_timeline[n_posts]
        recent_at = as_datetime(recent["created_at"])

        # can use created_after param for filtering out posts:
        partial_pull = list(
            api.pull_statuses(
                username=username, replies=False, created_after=recent_at, verbose=True
            )
        )
        assert len(partial_pull) == n_posts
        assert recent["id"] not in [post["id"] for post in partial_pull]

        # can use since_id param for filtering out posts:
        partial_pull = list(
            api.pull_statuses(
                username=username, replies=False, since_id=recent["id"], verbose=True
            )
        )
        assert len(partial_pull) == n_posts
        assert recent["id"] not in [post["id"] for post in partial_pull]

        # POST INFO
        # contains status info
        assert list(latest.keys()) == [
            'id',
             'created_at',
             'in_reply_to_id',
             'quote_id',
             'in_reply_to_account_id',
             'sensitive',
             'spoiler_text',
             'visibility',
             'language',
             'uri',
             'url',
             'content',
             'account',
             'media_attachments',
             'mentions',
             'tags',
             'card',
             'group',
             'quote',
             'in_reply_to',
             'reblog',
             'sponsored',
             'replies_count',
             'reblogs_count',
             'favourites_count',
             'reaction',
             'upvotes_count',
             'downvotes_count',
             'favourited',
             'reblogged',
             'muted',
             'pinned',
             'bookmarked',
             'poll',
             'emojis',
             'votable',
             '_pulled'
                ]
        assert isinstance(latest["id"], str)
        latest_post=latest["id"]
        print(latest)
        # api.user_likes(post=latest_post)
        time.sleep(30)

