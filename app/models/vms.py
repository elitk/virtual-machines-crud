from datetime import datetime
from app.extensions import db


class VM(db.Model):
    __tablename__ = 'vms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    uuid = db.Column(db.String(36), unique=True, nullable=False)
    memory = db.Column(db.Integer, default=2048)  # in MB
    cpus = db.Column(db.Integer, default=2)
    os_type = db.Column(db.String(50))
    status = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), default=1)

    user = db.relationship('User', backref=db.backref('vms', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'uuid': self.uuid,
            'memory': self.memory,
            'cpus': self.cpus,
            'os_type': self.os_type,
            'status': self.status
        }