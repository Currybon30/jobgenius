from app.db.base import Base
from sqlalchemy import BigInteger, Column, DateTime, String


class User(Base):
    __tablename__ = "users"
    uid = Column(BigInteger, primary_key=True, index=True)
    plan = Column(String(50), nullable=False, default="FREE")
    plan_expiry = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"User(uid={self.uid}, plan='{self.plan}', plan_expiry={self.plan_expiry})"
