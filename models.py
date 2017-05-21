from slack import db


# Create our database model
class Org(db.Model):
    __tablename__ = "organizations"
    id = db.Column(db.Integer, primary_key=True)
    org = db.Column(db.String(120), unique=True)

    def __init__(self, org=None):
        self.org_name = org

    def __repr__(self):
        return '<id {}>'.format(self.id)

