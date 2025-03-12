from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def set_password(self, new_password):
        """Cập nhật mật khẩu mới (được hash)"""
        self.password = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.session.commit()

    def check_password(self, password):
        return check_password_hash(self.password, password)
