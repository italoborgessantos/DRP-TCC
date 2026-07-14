from sqlalchemy import func
from models.database import BaseModel
from sqlalchemy import Column, Integer, String, DateTime
from werkzeug.security import generate_password_hash, check_password_hash


class Employee(BaseModel):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(12), nullable=True)
    registered_on = Column(DateTime(
        timezone=True), nullable=False, default=func.now())

    password = Column(String(255), nullable=False)

    def __init__(self, name, email, password, phone=None):
        self.name = name
        self.email = email
        self.phone = phone
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)
