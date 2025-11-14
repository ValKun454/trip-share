from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Double
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)

    trips = relationship('Trip', back_populates='creator')
    expenses = relationship('Expense', back_populates='payer')
    positions = relationship('Position', back_populates='participant')

class Trip(Base):
    __tablename__ = 'trips'

    id = Column(Integer, primary_key=True, index=True)
    link = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, unique=True, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    creator_id = Column(Integer, ForeignKey('users.id'))

    creator = relationship('User', back_populates='trips')
    expenses = relationship('Expense', back_populates='trip')

class Expense(Base):
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True, index=True)
    is_scanned = Column(Boolean, default=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, unique=True, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    trip_id = Column(Integer, ForeignKey('trips.id'))
    payer_id = Column(Integer, ForeignKey('users.id'))
    is_even_division = Column(Boolean, default=True, nullable=False)
    total_cost = Column(Double, index=True, nullable=False)

    trip = relationship('Trip', back_populates='expenses')
    payer = relationship('User', back_populates='expenses')
    positions = relationship('Position', back_populates='expense')

class Position(Base):
    __tablename__ = 'positions'

    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey('expenses.id'))
    participant_id = Column(Integer, ForeignKey('users.id'))

    expense = relationship('Expense', back_populates='positions')
    participant = relationship('User', back_populates='positions')
