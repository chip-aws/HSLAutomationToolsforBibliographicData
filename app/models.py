# converting a post to a JSON serializable dictionary
from flask_login import UserMixin, AnonymousUserMixin

# converting a user to a JSON serializable dictionary
# class User(UserMixin, db.Model):
class User(UserMixin):

    # ...
    def to_json(self):
        json_user = {
                'url': url_for('api.get_user', id=self.id),
                'username': self.username,
                'member_since': self.member_since,
                'last_seen': self.last_seen,
                'posts_url': url_for('api.get_user_posts', id=self.id),
                'followed_posts_url': url_for('api.get_user_followed_posts',
                                              id=self.id),
                'post_count': self.posts.count()
                }
        return json_user

