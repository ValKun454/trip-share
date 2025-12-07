from sqlalchemy import Column, String, Integer, Boolean, DateTime, Date, ForeignKey, Numeric, UniqueConstraint, CheckConstraint, ForeignKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    username = Column(String(40), unique=True, index=True, nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)

    trips_user = relationship('Trip', back_populates='creator')
    expenses = relationship('Expense', back_populates='payer')
    trips = relationship("Participant", back_populates="user")

class Trip(Base):
    __tablename__ = 'trips'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), index=True, nullable=True)
    beginning_date = Column(Date, index=True, nullable=True)
    end_date = Column(Date, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    creator_id = Column(Integer, ForeignKey('users.id'))

    _participants = relationship("Participant", back_populates="trip", cascade="all, delete-orphan")
    creator = relationship('User', back_populates='trips_user')
    expenses = relationship('Expense', back_populates='trip', cascade="all, delete-orphan")
    trip_invites = relationship('TripInvite', back_populates='trip', cascade="all, delete-orphan")
    
    # 2. This is the "fake" property Pydantic will read.
    #    It formats the data just as you want it.
    @property
    def participants(self) -> list[int]:
        # This loops through the list of Participant objects
        # and returns only the user_id for each one.
        return [p.user_id for p in self._participants]

class Participant(Base):
    __tablename__ = 'participants'
    
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    trip_id = Column(Integer, ForeignKey('trips.id'), primary_key=True)

    user = relationship("User", back_populates="trips")
    trip = relationship("Trip", back_populates="_participants")
    shares = relationship("ParticipantShare", back_populates="participant")

class Expense(Base):
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True, index=True)
    is_scanned = Column(Boolean, default=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500), index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    trip_id = Column(Integer, ForeignKey('trips.id'))
    payer_id = Column(Integer, ForeignKey('users.id'))
    is_even_division = Column(Boolean, default=True, nullable=False)
    total_cost = Column(Numeric(precision=20, scale=2), index=True, nullable=False)

    trip = relationship('Trip', back_populates='expenses')
    payer = relationship('User', back_populates='expenses')
    shares = relationship('ParticipantShare', back_populates='expense', cascade="all, delete-orphan")


class Friend(Base):
    __tablename__ = 'friends'

    id = Column(Integer, primary_key=True)
    user_id_1 = Column(Integer, ForeignKey('users.id'), nullable=False)
    user_id_2 = Column(Integer, ForeignKey('users.id'), nullable=False)
    is_accepted = Column(Boolean, default=False, nullable=False)
    initiator_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    __table_args__ = (
        UniqueConstraint('user_id_1', 'user_id_2', name='unique_friendship'),
        # Ensure user_id_1 is always less than user_id_2
        CheckConstraint('user_id_1 < user_id_2', name='check_user_order'),
    )

class TripInvite(Base):
    __tablename__ = 'trip_invites'

    id = Column(Integer, primary_key=True)
    trip_id = Column(Integer, ForeignKey('trips.id'), nullable=False)
    invitee_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    inviter_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    status = Column(String(20), nullable=False, default='pending')
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    trip = relationship('Trip')
    invitee = relationship('User', foreign_keys=[invitee_id])
    inviter = relationship('User', foreign_keys=[inviter_id])

    __table_args__ = (
        UniqueConstraint('trip_id', 'invitee_id', name='unique_trip_invite'),
        CheckConstraint("status IN ('pending', 'accepted', 'declined')", name='check_status'),
    )

class ParticipantShare(Base):
    __tablename__ = 'participant_shares'

    user_id = Column(Integer, primary_key=True)
    trip_id = Column(Integer, primary_key=True)
    expense_id = Column(Integer, ForeignKey('expenses.id'), primary_key=True)
    is_paying = Column(Boolean, default=False, nullable=False)
    amount = Column(Numeric(precision=20, scale=2), default=0.0, nullable=False)

    participant = relationship("Participant", back_populates="shares", 
                             foreign_keys=[user_id, trip_id])
    expense = relationship("Expense", back_populates="shares")
    
    __table_args__ = (
        ForeignKeyConstraint(['user_id', 'trip_id'], ['participants.user_id', 'participants.trip_id']),
    )