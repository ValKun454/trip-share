from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
import uvicorn
from datetime import timedelta
from schemas import *
from auth import authenticate_user, create_access_token, get_current_user, get_db, ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash
from models import User, Trip as TripModel, Participant, Expense as ExpenseModel, Friend, TripInvite, ParticipantShare
from email_utils import create_verification_token, verify_verification_token, send_verification_email
from decimal import Decimal, ROUND_DOWN


app = FastAPI()

prefix_router = APIRouter(prefix="/api")



# Enable CORS so your frontend can talk to the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@prefix_router.get("/")
def read_root():
    return {"message": "Hello from FastAPI!"}

# Authentication endpoints
@prefix_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user
    - Email must be unique
    - Username must be unique
    - Password must be at least 8 characters
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if username already exists
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        is_verified=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Send verification email
    verification_token = create_verification_token(new_user.email)
    send_verification_email(new_user.email, new_user.username, verification_token)

    return new_user

@prefix_router.get("/verify")
async def verify_email(token: str, db: Session = Depends(get_db)):
    """
    Email verification endpoint
    User clicks link in email with verification token
    """
    # Verify the token
    email = verify_verification_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )

    # Find user by email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if already verified
    if user.is_verified:
        return {"message": "Email already verified"}

    # Mark as verified
    user.is_verified = True
    db.commit()

    return {"message": "Email successfully verified! You can now log in."}

@prefix_router.post("/resend-verification")
async def resend_verification(email_data: dict, db: Session = Depends(get_db)):
    """
    Resend verification email
    Body: {"email": "user@example.com"}
    """
    email = email_data.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is required"
        )

    # Find user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Don't reveal if user exists or not for security
        return {"message": "If the email exists, a verification link has been sent"}

    # Check if already verified
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )

    # Send verification email
    verification_token = create_verification_token(user.email)
    send_verification_email(user.email, user.username, verification_token)

    return {"message": "Verification email sent"}

@prefix_router.post("/login", response_model=Token)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login endpoint - accepts email and password as JSON
    Returns JWT access token
    Requires email to be verified
    """
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if email is verified
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please check your email and verify your account first."
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@prefix_router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current user info - protected endpoint
    Requires valid JWT token in Authorization header: Bearer <token>
    """
    return current_user

@prefix_router.put("/me", response_model=UserResponse)
async def update_user(
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update current user's information
    Can update email, username, and password
    Email and username must remain unique
    """
    # Update email if provided
    if data.email is not None and data.email != current_user.email:
        # Check if new email already exists
        existing_user = db.query(User).filter(User.email == data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = data.email
        # Reset verification status when email changes
        current_user.is_verified = False

    # Update username if provided
    if data.username is not None and data.username != current_user.username:
        # Check if new username already exists
        existing_username = db.query(User).filter(User.username == data.username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        current_user.username = data.username

    # Update password if provided
    if data.password is not None:
        hashed_password = get_password_hash(data.password)
        current_user.hashed_password = hashed_password

    db.commit()
    db.refresh(current_user)

    return current_user

@prefix_router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete current user's account
    Deletes all associated trips, participants, expenses, and positions
    This action is permanent and cannot be undone
    """
    # Delete the user (cascade will handle related data)
    db.delete(current_user)
    db.commit()

    return None

# Friend endpoints
@prefix_router.get("/friends", response_model=list[FriendResponse])
async def get_friends(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all friends for the current user
    Returns friendship records where current user is either user_id_1 or user_id_2
    """
    # Get all friendships involving the current user
    friendships = db.query(Friend).filter(
        (Friend.user_id_1 == current_user.id) | (Friend.user_id_2 == current_user.id)
    ).all()

    # Build response with friend usernames
    response_list = []
    for friendship in friendships:
        # Get the other user (the friend)
        other_user_id = friendship.user_id_2 if current_user.id == friendship.user_id_1 else friendship.user_id_1
        other_user = db.query(User).filter(User.id == other_user_id).first()

        response_list.append({
            "id": friendship.id,
            "user_id_1": friendship.user_id_1,
            "user_id_2": friendship.user_id_2,
            "is_accepted": friendship.is_accepted,
            "friend_username": other_user.username if other_user else None
        })

    return response_list

@prefix_router.get("/friends/list", response_model=list[FriendUser])
async def get_friends_list(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of accepted friends for the current user
    Returns only user id and username for each accepted friend
    """
    # Get all accepted friendships involving the current user
    friendships = db.query(Friend).filter(
        ((Friend.user_id_1 == current_user.id) | (Friend.user_id_2 == current_user.id)),
        Friend.is_accepted == True
    ).all()

    # Extract friend user IDs
    friend_ids = []
    for friendship in friendships:
        if friendship.user_id_1 == current_user.id:
            friend_ids.append(friendship.user_id_2)
        else:
            friend_ids.append(friendship.user_id_1)

    # Get user details for all friends
    friends = db.query(User).filter(User.id.in_(friend_ids)).all()

    # Return only id and username
    return [{"id": friend.id, "username": friend.username} for friend in friends]

@prefix_router.post("/friends", response_model=FriendResponse, status_code=status.HTTP_201_CREATED)
async def add_friend(
    data: FriendCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send a friend request to another user
    Creates a pending friendship (is_accepted=False) between current user and the specified friend_id
    Current user is always user_id_1, friend is user_id_2 (after ordering constraint)
    """
    # Verify friend exists
    friend_user = db.query(User).filter(User.id == data.friend_id).first()
    if not friend_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {data.friend_id} not found"
        )

    # Prevent users from adding themselves as friends
    if current_user.id == data.friend_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add yourself as a friend"
        )

    # Ensure user_id_1 < user_id_2 to satisfy database constraint
    user_id_1 = min(current_user.id, data.friend_id)
    user_id_2 = max(current_user.id, data.friend_id)

    # Check if friendship or friend request already exists
    existing_friendship = db.query(Friend).filter(
        Friend.user_id_1 == user_id_1,
        Friend.user_id_2 == user_id_2
    ).first()

    if existing_friendship:
        if existing_friendship.is_accepted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Friendship already exists"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Friend request already sent"
            )

    # Create the pending friend request
    new_friendship = Friend(
        user_id_1=user_id_1,
        user_id_2=user_id_2,
        is_accepted=False,
        initiator_id=current_user.id
    )

    db.add(new_friendship)
    db.commit()
    db.refresh(new_friendship)

    # Convert to dict and add friend username
    response_data = {
        "id": new_friendship.id,
        "user_id_1": new_friendship.user_id_1,
        "user_id_2": new_friendship.user_id_2,
        "is_accepted": new_friendship.is_accepted,
        "friend_username": friend_user.username
    }

    return response_data

@prefix_router.put("/friends/{friendship_id}/accept", response_model=FriendResponse)
async def accept_friend_request(
    friendship_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Accept a friend request
    Only the recipient of the friend request (not the initiator) can accept it
    Sets is_accepted to True
    """
    # Get the friendship
    friendship = db.query(Friend).filter(Friend.id == friendship_id).first()

    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friend request not found"
        )

    # Check if current user is part of this friendship
    if current_user.id != friendship.user_id_1 and current_user.id != friendship.user_id_2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not part of this friend request"
        )

    # Check if current user is the initiator (they cannot accept their own request)
    if current_user.id == friendship.initiator_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot accept your own friend request"
        )

    # Check if already accepted
    if friendship.is_accepted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Friend request already accepted"
        )

    # Accept the friend request
    friendship.is_accepted = True
    db.commit()
    db.refresh(friendship)

    # Get the other user's info
    other_user_id = friendship.user_id_2 if current_user.id == friendship.user_id_1 else friendship.user_id_1
    other_user = db.query(User).filter(User.id == other_user_id).first()

    # Return response with friend username
    response_data = {
        "id": friendship.id,
        "user_id_1": friendship.user_id_1,
        "user_id_2": friendship.user_id_2,
        "is_accepted": friendship.is_accepted,
        "friend_username": other_user.username if other_user else None
    }

    return response_data

@prefix_router.get("/friends/requests", response_model=list[FriendResponse])
async def get_friend_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all incoming pending friend requests for the current user
    Returns friend requests where current user is the recipient (not the initiator)
    """
    # Get all pending friend requests where current user is the recipient (not the initiator)
    pending_requests = db.query(Friend).filter(
        ((Friend.user_id_1 == current_user.id) | (Friend.user_id_2 == current_user.id)),
        Friend.is_accepted == False,
        Friend.initiator_id != current_user.id
    ).all()

    # Build response with friend usernames
    response_list = []
    for request in pending_requests:
        # Get the other user (the one who sent the request)
        other_user_id = request.user_id_2 if current_user.id == request.user_id_1 else request.user_id_1
        other_user = db.query(User).filter(User.id == other_user_id).first()

        response_list.append({
            "id": request.id,
            "user_id_1": request.user_id_1,
            "user_id_2": request.user_id_2,
            "is_accepted": request.is_accepted,
            "friend_username": other_user.username if other_user else None
        })

    return response_list

@prefix_router.delete("/friends/{friend_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_friend(
    friend_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove a friend for the current user
    Deletes the friendship between current user and the specified friend_id
    """
    # Verify friend exists
    friend_user = db.query(User).filter(User.id == friend_id).first()
    if not friend_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {friend_id} not found"
        )

    # Determine the correct order for querying
    user_id_1 = min(current_user.id, friend_id)
    user_id_2 = max(current_user.id, friend_id)

    # Find the friendship
    friendship = db.query(Friend).filter(
        Friend.user_id_1 == user_id_1,
        Friend.user_id_2 == user_id_2
    ).first()

    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friendship not found"
        )

    # Delete the friendship
    db.delete(friendship)
    db.commit()

    return None


# Trip Invite endpoints
@prefix_router.post("/trips/{trip_id}/invites", response_model=TripInviteResponse, status_code=status.HTTP_201_CREATED)
async def invite_user_to_trip(
    trip_id: int,
    data: TripInviteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Invite a user to a trip
    Only the trip creator or participants can invite users
    Can only invite users from the friend list (accepted friends)
    """
    # Verify the trip exists
    trip = db.query(TripModel).filter(TripModel.id == trip_id).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )

    # Check if current user has access to this trip
    is_creator = trip.creator_id == current_user.id
    is_participant = db.query(Participant).filter(
        Participant.trip_id == trip_id,
        Participant.user_id == current_user.id
    ).first() is not None

    if not is_creator and not is_participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this trip"
        )

    # Verify invitee exists
    invitee = db.query(User).filter(User.id == data.invitee_id).first()
    if not invitee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {data.invitee_id} not found"
        )

    # Check if invitee is a friend (accepted friendship)
    user_id_1 = min(current_user.id, data.invitee_id)
    user_id_2 = max(current_user.id, data.invitee_id)

    friendship = db.query(Friend).filter(
        Friend.user_id_1 == user_id_1,
        Friend.user_id_2 == user_id_2,
        Friend.is_accepted == True
    ).first()

    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only invite users from your friend list"
        )

    # Check if user is already a participant or creator
    if trip.creator_id == data.invitee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already the creator of this trip"
        )

    existing_participant = db.query(Participant).filter(
        Participant.trip_id == trip_id,
        Participant.user_id == data.invitee_id
    ).first()

    if existing_participant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a participant of this trip"
        )

    # Check if invite already exists
    existing_invite = db.query(TripInvite).filter(
        TripInvite.trip_id == trip_id,
        TripInvite.invitee_id == data.invitee_id
    ).first()

    if existing_invite:
        if existing_invite.status == 'pending':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invite already sent to this user"
            )
        elif existing_invite.status == 'accepted':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User has already accepted an invite to this trip"
            )
        elif existing_invite.status == 'declined':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User has declined an invite to this trip"
            )

    # Create the invite
    new_invite = TripInvite(
        trip_id=trip_id,
        invitee_id=data.invitee_id,
        inviter_id=current_user.id,
        status='pending'
    )

    db.add(new_invite)
    db.commit()
    db.refresh(new_invite)

    # Build response with additional info
    response_data = {
        "id": new_invite.id,
        "trip_id": new_invite.trip_id,
        "invitee_id": new_invite.invitee_id,
        "inviter_id": new_invite.inviter_id,
        "status": new_invite.status,
        "created_at": new_invite.created_at,
        "trip_name": trip.name,
        "invitee_username": invitee.username,
        "inviter_username": current_user.username
    }

    return response_data

@prefix_router.put("/trips/invites/{invite_id}", response_model=TripInviteResponse)
async def respond_to_trip_invite(
    invite_id: int,
    data: TripInviteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Accept or decline a trip invite
    Only the invitee can respond to the invite
    Status must be 'accepted' or 'declined'
    When accepted, creates ParticipantShare records for all existing expenses
    """
    # Validate status
    if data.status not in ['accepted', 'declined']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be 'accepted' or 'declined'"
        )

    # Get the invite
    invite = db.query(TripInvite).filter(TripInvite.id == invite_id).first()
    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invite not found"
        )

    # Check if current user is the invitee
    if invite.invitee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the invitee can respond to this invite"
        )

    # Check if invite is still pending
    if invite.status != 'pending':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invite has already been {invite.status}"
        )

    # Update the invite status
    invite.status = data.status

    # If accepted, add user as participant and create shares for existing expenses
    if data.status == 'accepted':
        # Check if user is already a participant
        existing_participant = db.query(Participant).filter(
            Participant.trip_id == invite.trip_id,
            Participant.user_id == current_user.id
        ).first()

        if not existing_participant:
            new_participant = Participant(
                user_id=current_user.id,
                trip_id=invite.trip_id
            )
            db.add(new_participant)
            db.flush()  # Flush to make participant available for foreign key

        # Get all existing expenses for this trip
        existing_expenses = db.query(ExpenseModel).filter(
            ExpenseModel.trip_id == invite.trip_id
        ).all()

        # Create ParticipantShare for each existing expense
        for expense in existing_expenses:
            # Check if share already exists (shouldn't happen, but be safe)
            existing_share = db.query(ParticipantShare).filter(
                ParticipantShare.expense_id == expense.id,
                ParticipantShare.user_id == current_user.id
            ).first()

            if not existing_share:
                new_share = ParticipantShare(
                    user_id=current_user.id,
                    trip_id=invite.trip_id,
                    expense_id=expense.id,
                    is_paying=False,  # Default to not paying
                    amount=Decimal('0.0')  # Default amount is 0
                )
                db.add(new_share)

    db.commit()
    db.refresh(invite)

    # Get additional info for response
    trip = db.query(TripModel).filter(TripModel.id == invite.trip_id).first()
    invitee = db.query(User).filter(User.id == invite.invitee_id).first()
    inviter = db.query(User).filter(User.id == invite.inviter_id).first()

    response_data = {
        "id": invite.id,
        "trip_id": invite.trip_id,
        "invitee_id": invite.invitee_id,
        "inviter_id": invite.inviter_id,
        "status": invite.status,
        "created_at": invite.created_at,
        "trip_name": trip.name if trip else None,
        "invitee_username": invitee.username if invitee else None,
        "inviter_username": inviter.username if inviter else None
    }

    return response_data

@prefix_router.get("/trips/invites", response_model=list[TripInviteResponse])
async def get_incoming_trip_invites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all incoming trip invites for the current user
    Returns only pending invites where current user is the invitee
    """
    # Get all pending invites for the current user
    invites = db.query(TripInvite).filter(
        TripInvite.invitee_id == current_user.id,
        TripInvite.status == 'pending'
    ).all()

    # Build response list with additional info
    response_list = []
    for invite in invites:
        trip = db.query(TripModel).filter(TripModel.id == invite.trip_id).first()
        inviter = db.query(User).filter(User.id == invite.inviter_id).first()

        response_list.append({
            "id": invite.id,
            "trip_id": invite.trip_id,
            "invitee_id": invite.invitee_id,
            "inviter_id": invite.inviter_id,
            "status": invite.status,
            "created_at": invite.created_at,
            "trip_name": trip.name if trip else None,
            "invitee_username": current_user.username,
            "inviter_username": inviter.username if inviter else None
        })

    return response_list


# GET endpoint - retrieve data  ---- trip


@prefix_router.get("/trips/{trip_id}", response_model=Trip)
def get_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific trip by ID
    Only returns trip if current user is creator or participant
    """
    # Query the trip
    trip = db.query(TripModel).filter(TripModel.id == trip_id).first()

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )

    # Check if user has access (is creator or participant)
    is_creator = trip.creator_id == current_user.id
    is_participant = db.query(Participant).filter(
        Participant.trip_id == trip_id,
        Participant.user_id == current_user.id
    ).first() is not None

    if not is_creator and not is_participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this trip"
        )

    return trip

@prefix_router.get("/trips", response_model=list[Trip])
def get_trips(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all trips for the current user
    Returns trips where user is creator or participant
    """
    # Get trips where user is creator
    creator_trips = db.query(TripModel).filter(
        TripModel.creator_id == current_user.id
    ).all()

    # Get trips where user is participant
    participant_trip_ids = db.query(Participant.trip_id).filter(
        Participant.user_id == current_user.id
    ).all()
    participant_trip_ids = [t[0] for t in participant_trip_ids]

    participant_trips = db.query(TripModel).filter(
        TripModel.id.in_(participant_trip_ids)
    ).all() if participant_trip_ids else []

    # Combine and deduplicate (in case user is both creator and participant)
    all_trips = {trip.id: trip for trip in creator_trips + participant_trips}

    return list(all_trips.values())

@prefix_router.post("/trips", response_model=TripCreateResponse, status_code=status.HTTP_201_CREATED)
def create_trip(
    data: TripCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new trip
    Current user becomes the creator and is automatically added as a participant
    To add other participants, use the invite system after creation
    """
    # Create the trip
    new_trip = TripModel(
        name=data.name,
        description=data.description,
        beginning_date=data.beginning_date,
        end_date=data.end_date,
        creator_id=current_user.id
    )

    db.add(new_trip)
    db.commit()
    db.refresh(new_trip)

    # Add creator as a participant
    creator_participant = Participant(
        user_id=current_user.id,
        trip_id=new_trip.id
    )
    db.add(creator_participant)
    db.commit()
    db.refresh(new_trip)

    return new_trip

@prefix_router.put("/trips/{trip_id}", response_model=Trip)
def update_trip(
    trip_id: int,
    data: TripUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing trip
    Only the creator can update the trip
    Can update name, description, and dates
    To manage participants, use the invite system
    """
    # Query the trip
    trip = db.query(TripModel).filter(TripModel.id == trip_id).first()

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )

    # Check if user is the creator
    if trip.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the trip creator can update the trip"
        )

    # Update trip fields if provided
    if data.name is not None:
        trip.name = data.name
    if data.description is not None:
        trip.description = data.description
    if data.beginning_date is not None:
        trip.beginning_date = data.beginning_date
    if data.end_date is not None:
        trip.end_date = data.end_date

    # Note: participants management removed
    # Users must use /trips/{trip_id}/invites to manage participants

    db.commit()
    db.refresh(trip)

    return trip

@prefix_router.delete("/trips/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a trip
    Only the creator can delete the trip
    Deletes all associated participants and expenses
    """
    # Query the trip
    trip = db.query(TripModel).filter(TripModel.id == trip_id).first()

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )

    # Check if user is the creator
    if trip.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the trip creator can delete the trip"
        )

    # Delete the trip (cascade will handle participants and expenses)
    db.delete(trip)
    db.commit()

    return None



@prefix_router.get("/trips/{trip_id}/expenses", response_model=list[Expense])
def get_expenses(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all expenses for a specific trip
    Only returns expenses if current user has access to the trip
    Includes participant shares for each expense
    """
    # First verify the trip exists and user has access
    trip = db.query(TripModel).filter(TripModel.id == trip_id).first()

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )

    # Check if user has access to this trip
    is_creator = trip.creator_id == current_user.id
    is_participant = db.query(Participant).filter(
        Participant.trip_id == trip_id,
        Participant.user_id == current_user.id
    ).first() is not None

    if not is_creator and not is_participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this trip"
        )

    # Get all expenses for this trip
    expenses = db.query(ExpenseModel).filter(
        ExpenseModel.trip_id == trip_id
    ).all()

    # Build response with participant shares
    response_list = []
    for expense in expenses:
        # Get participant shares for this expense
        shares = db.query(ParticipantShare).filter(
            ParticipantShare.expense_id == expense.id
        ).all()

        # Build shares list with usernames
        shares_list = []
        for share in shares:
            user = db.query(User).filter(User.id == share.user_id).first()
            shares_list.append({
                "username": user.username if user else None,
                "is_paying": share.is_paying,
                "amount": str(share.amount)
            })

        expense_dict = {
            "id": expense.id,
            "is_scanned": expense.is_scanned,
            "name": expense.name,
            "description": expense.description,
            "created_at": expense.created_at,
            "trip_id": expense.trip_id,
            "payer_id": expense.payer_id,
            "is_even_division": expense.is_even_division,
            "total_cost": expense.total_cost,
            "participant_shares": shares_list
        }
        response_list.append(expense_dict)

    return response_list


def calculate_even_division(total_cost: Decimal, paying_shares: list) -> dict[int, Decimal]:
    """
    Calculate even division of total_cost among paying participants.
    Returns dict mapping user_id to amount.
    Adds remainder to first participant.
    """
    num_paying = len(paying_shares)
    if num_paying == 0:
        return {}
    
    # Calculate base amount (rounded down to 2 decimal places)
    base_amount = (total_cost / num_paying).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
    
    # Calculate remainder
    total_distributed = base_amount * num_paying
    remainder = total_cost - total_distributed
    
    # Create amounts dict
    amounts = {}
    for i, share in enumerate(paying_shares):
        if i == 0:
            # First participant gets base amount + remainder
            amounts[share.user_id] = base_amount + remainder
        else:
            amounts[share.user_id] = base_amount
    
    return amounts

@prefix_router.post("/trips/{trip_id}/expenses", response_model=ExpenseCreateResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    trip_id: int,
    data: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new expense for a trip
    Only allowed if current user has access to the trip
    
    If is_even_division=True:
    - Amount in participant_shares is ignored
    - total_cost is split evenly among participants where is_paying=True
    - Remainder is added to first paying participant
    
    If is_even_division=False:
    - Sum of amounts for is_paying=True must equal total_cost
    """
    # Verify the trip exists and user has access
    trip = db.query(TripModel).filter(TripModel.id == trip_id).first()

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )

    # Check if user has access to this trip
    is_creator = trip.creator_id == current_user.id
    is_participant = db.query(Participant).filter(
        Participant.trip_id == trip_id,
        Participant.user_id == current_user.id
    ).first() is not None

    if not is_creator and not is_participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this trip"
        )

    # Verify payer exists and is part of the trip
    payer = db.query(User).filter(User.id == data.payer_id).first()
    if not payer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payer with id {data.payer_id} not found"
        )

    # Check if payer is creator or participant of the trip
    payer_is_creator = trip.creator_id == data.payer_id
    payer_is_participant = db.query(Participant).filter(
        Participant.trip_id == trip_id,
        Participant.user_id == data.payer_id
    ).first() is not None

    if not payer_is_creator and not payer_is_participant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payer must be a participant of the trip"
        )

    # Validate participant_shares
    if not data.participant_shares:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="participant_shares is required and cannot be empty"
        )

    # Get all participants for this trip (including creator)
    participants = db.query(Participant).filter(
        Participant.trip_id == trip_id
    ).all()
    
    participant_ids = [p.user_id for p in participants]
    if trip.creator_id not in participant_ids:
        participant_ids.append(trip.creator_id)

    # Validate that all users in participant_shares are trip participants
    share_user_ids = [share.user_id for share in data.participant_shares]
    for user_id in share_user_ids:
        if user_id not in participant_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User {user_id} is not a participant of this trip"
            )

    # Handle even division vs custom amounts
    if data.is_even_division:
        # Filter paying shares
        paying_shares = [share for share in data.participant_shares if share.is_paying]
        
        if not paying_shares:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one participant must be paying"
            )
        
        # Calculate even division
        share_amounts = calculate_even_division(data.total_cost, paying_shares)
    else:
        # Validate that sum of paying amounts equals total_cost
        total_paying = sum(
            share.amount for share in data.participant_shares if share.is_paying
        )
        
        if total_paying != data.total_cost:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Sum of amounts for paying participants ({total_paying}) must equal total cost ({data.total_cost})"
            )
        
        # Use provided amounts
        share_amounts = {
            share.user_id: share.amount 
            for share in data.participant_shares 
            if share.is_paying
        }

    # Create the expense
    new_expense = ExpenseModel(
        is_scanned=data.is_scanned,
        name=data.name,
        description=data.description,
        trip_id=trip_id,
        payer_id=data.payer_id,
        is_even_division=data.is_even_division,
        total_cost=data.total_cost
    )

    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)

    # Create participant shares with calculated/provided amounts
    for share_data in data.participant_shares:
        amount = share_amounts.get(share_data.user_id, Decimal('0.0')) if share_data.is_paying else Decimal('0.0')
        
        share = ParticipantShare(
            user_id=share_data.user_id,
            trip_id=trip_id,
            expense_id=new_expense.id,
            is_paying=share_data.is_paying,
            amount=amount
        )
        db.add(share)

    db.commit()
    db.refresh(new_expense)

    # Get participant shares for response
    shares = db.query(ParticipantShare).filter(
        ParticipantShare.expense_id == new_expense.id
    ).all()

    shares_list = []
    for share in shares:
        user = db.query(User).filter(User.id == share.user_id).first()
        shares_list.append({
            "username": user.username if user else None,
            "is_paying": share.is_paying,
            "amount": str(share.amount)
        })

    response_data = {
        "id": new_expense.id,
        "is_scanned": new_expense.is_scanned,
        "name": new_expense.name,
        "description": new_expense.description,
        "created_at": new_expense.created_at,
        "trip_id": new_expense.trip_id,
        "payer_id": new_expense.payer_id,
        "is_even_division": new_expense.is_even_division,
        "total_cost": new_expense.total_cost,
        "participant_shares": shares_list
    }

    return response_data


@prefix_router.put("/trips/{trip_id}/expenses/{expense_id}", response_model=Expense)
def update_expense(
    trip_id: int,
    expense_id: int,
    data: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing expense
    Only allowed if current user has access to the trip
    
    If is_even_division=True:
    - Amount in participant_shares is ignored
    - total_cost is split evenly among participants where is_paying=True
    - Remainder is added to first paying participant
    - Shares are automatically recalculated when total_cost changes
    
    If is_even_division=False:
    - Sum of amounts for is_paying=True must equal total_cost
    - Sets amount to 0.0 for all shares where is_paying=False
    """
    # Verify the trip exists and user has access
    trip = db.query(TripModel).filter(TripModel.id == trip_id).first()

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )

    # Check if user has access to this trip
    is_creator = trip.creator_id == current_user.id
    is_participant = db.query(Participant).filter(
        Participant.trip_id == trip_id,
        Participant.user_id == current_user.id
    ).first() is not None

    if not is_creator and not is_participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this trip"
        )

    # Query the expense
    expense = db.query(ExpenseModel).filter(
        ExpenseModel.id == expense_id,
        ExpenseModel.trip_id == trip_id
    ).first()

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )

    # Track if we need to recalculate shares
    needs_recalculation = False
    
    # Update expense fields if provided
    if data.is_scanned is not None:
        expense.is_scanned = data.is_scanned
    if data.name is not None:
        expense.name = data.name
    if data.description is not None:
        expense.description = data.description
    if data.is_even_division is not None:
        if expense.is_even_division != data.is_even_division:
            needs_recalculation = True
        expense.is_even_division = data.is_even_division
    if data.total_cost is not None:
        if expense.total_cost != data.total_cost:
            needs_recalculation = True
        expense.total_cost = data.total_cost

    # Update payer if provided
    if data.payer_id is not None:
        # Verify payer exists and is part of the trip
        payer = db.query(User).filter(User.id == data.payer_id).first()
        if not payer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payer with id {data.payer_id} not found"
            )

        # Check if payer is creator or participant of the trip
        payer_is_creator = trip.creator_id == data.payer_id
        payer_is_participant = db.query(Participant).filter(
            Participant.trip_id == trip_id,
            Participant.user_id == data.payer_id
        ).first() is not None

        if not payer_is_creator and not payer_is_participant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payer must be a participant of the trip"
            )

        expense.payer_id = data.payer_id

    db.commit()

    # Update participant shares if provided in request OR if recalculation is needed
    if data.participant_shares is not None:
        # Handle even division vs custom amounts
        if expense.is_even_division:
            # Filter paying shares
            paying_shares = [share for share in data.participant_shares if share.is_paying]
            
            if not paying_shares:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="At least one participant must be paying"
                )
            
            # Calculate even division
            share_amounts = calculate_even_division(expense.total_cost, paying_shares)
        else:
            # Validate that sum of paying amounts equals total_cost
            total_paying = sum(
                share.amount for share in data.participant_shares if share.is_paying
            )
            
            if total_paying != expense.total_cost:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Sum of amounts for paying participants ({total_paying}) must equal total cost ({expense.total_cost})"
                )
            
            # Use provided amounts
            share_amounts = {
                share.user_id: share.amount 
                for share in data.participant_shares 
                if share.is_paying
            }

        # Update each participant share
        for share_update in data.participant_shares:
            share = db.query(ParticipantShare).filter(
                ParticipantShare.expense_id == expense_id,
                ParticipantShare.user_id == share_update.user_id
            ).first()

            if not share:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Participant share for user {share_update.user_id} not found"
                )

            share.is_paying = share_update.is_paying
            share.amount = share_amounts.get(share_update.user_id, Decimal('0.0')) if share_update.is_paying else Decimal('0.0')

        db.commit()
    
    elif needs_recalculation and expense.is_even_division:
        # Automatically recalculate shares when total_cost or is_even_division changes
        # and is_even_division is True
        existing_shares = db.query(ParticipantShare).filter(
            ParticipantShare.expense_id == expense_id
        ).all()
        
        # Filter paying shares
        paying_shares = [share for share in existing_shares if share.is_paying]
        
        if paying_shares:
            # Calculate even division with updated total_cost
            share_amounts = calculate_even_division(expense.total_cost, paying_shares)
            
            # Update amounts for all shares
            for share in existing_shares:
                if share.is_paying:
                    share.amount = share_amounts.get(share.user_id, Decimal('0.0'))
                else:
                    share.amount = Decimal('0.0')
            
            db.commit()

    db.refresh(expense)

    # Get updated shares for response
    updated_shares = db.query(ParticipantShare).filter(
        ParticipantShare.expense_id == expense_id
    ).all()

    shares_list = []
    for share in updated_shares:
        user = db.query(User).filter(User.id == share.user_id).first()
        shares_list.append({
            "username": user.username if user else None,
            "is_paying": share.is_paying,
            "amount": str(share.amount)
        })

    response_data = {
        "id": expense.id,
        "is_scanned": expense.is_scanned,
        "name": expense.name,
        "description": expense.description,
        "created_at": expense.created_at,
        "trip_id": expense.trip_id,
        "payer_id": expense.payer_id,
        "is_even_division": expense.is_even_division,
        "total_cost": expense.total_cost,
        "participant_shares": shares_list
    }

    return response_data


@prefix_router.delete("/trips/{trip_id}/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    trip_id: int,
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an expense
    Only allowed if current user has access to the trip
    Automatically deletes associated participant shares (via cascade)
    """
    # Verify the trip exists and user has access
    trip = db.query(TripModel).filter(TripModel.id == trip_id).first()

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )

    # Check if user has access to this trip
    is_creator = trip.creator_id == current_user.id
    is_participant = db.query(Participant).filter(
        Participant.trip_id == trip_id,
        Participant.user_id == current_user.id
    ).first() is not None

    if not is_creator and not is_participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this trip"
        )

    # Query the expense
    expense = db.query(ExpenseModel).filter(
        ExpenseModel.id == expense_id,
        ExpenseModel.trip_id == trip_id
    ).first()

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )

    # Delete the expense (cascade will handle participant shares)
    db.delete(expense)
    db.commit()

    return None


@prefix_router.get("/trips/{trip_id}/owe", response_model=OweSummary)
def get_trip_owe_summary(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Calculate money owed for a trip
    Returns who owes money to current user and who current user owes money to
    """
    # Verify the trip exists and user has access
    trip = db.query(TripModel).filter(TripModel.id == trip_id).first()

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )

    # Check if user has access to this trip
    is_creator = trip.creator_id == current_user.id
    is_participant = db.query(Participant).filter(
        Participant.trip_id == trip_id,
        Participant.user_id == current_user.id
    ).first() is not None

    if not is_creator and not is_participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this trip"
        )

    # Get all expenses for this trip
    expenses = db.query(ExpenseModel).filter(
        ExpenseModel.trip_id == trip_id
    ).all()

    # Dictionaries to accumulate debts
    owe_to_me = {}  # {user_id: amount}
    i_owe_to = {}   # {user_id: amount}

    for expense in expenses:
        if expense.payer_id == current_user.id:
            # I paid for this expense - others may owe me
            shares = db.query(ParticipantShare).filter(
                ParticipantShare.expense_id == expense.id,
                ParticipantShare.is_paying == True,
                ParticipantShare.user_id != current_user.id
            ).all()

            for share in shares:
                if share.user_id not in owe_to_me:
                    owe_to_me[share.user_id] = Decimal('0.0')
                owe_to_me[share.user_id] += share.amount

        else:
            # Someone else paid - I may owe them
            my_share = db.query(ParticipantShare).filter(
                ParticipantShare.expense_id == expense.id,
                ParticipantShare.user_id == current_user.id,
                ParticipantShare.is_paying == True
            ).first()

            if my_share:
                payer_id = expense.payer_id
                if payer_id not in i_owe_to:
                    i_owe_to[payer_id] = Decimal('0.0')
                i_owe_to[payer_id] += my_share.amount

    # Get all trip participants (including creator)
    participants = db.query(Participant).filter(
        Participant.trip_id == trip_id
    ).all()
    
    participant_ids = [p.user_id for p in participants]
    if trip.creator_id not in participant_ids:
        participant_ids.append(trip.creator_id)
    
    # Remove current user from the list
    participant_ids = [pid for pid in participant_ids if pid != current_user.id]

    owe_to_me_list = []
    i_owe_to_list = []
    
    for user_id in participant_ids:
        user = db.query(User).filter(User.id == user_id).first()
        
        they_owe_me = owe_to_me.get(user_id, Decimal('0.0'))
        i_owe_them = i_owe_to.get(user_id, Decimal('0.0'))
        
        # Calculate net amount
        net_amount = they_owe_me - i_owe_them
        
        if net_amount > 0:
            # They owe me (net positive)
            owe_to_me_list.append({
                "user_id": user_id,
                "user_name": user.username if user else None,
                "amount": str(net_amount)
            })
            i_owe_to_list.append({
                "user_id": user_id,
                "user_name": user.username if user else None,
                "amount": "0.00"
            })
        elif net_amount < 0:
            # I owe them (net negative)
            owe_to_me_list.append({
                "user_id": user_id,
                "user_name": user.username if user else None,
                "amount": "0.00"
            })
            i_owe_to_list.append({
                "user_id": user_id,
                "user_name": user.username if user else None,
                "amount": str(abs(net_amount))
            })
        else:
            # Balanced - both zero
            owe_to_me_list.append({
                "user_id": user_id,
                "user_name": user.username if user else None,
                "amount": "0.00"
            })
            i_owe_to_list.append({
                "user_id": user_id,
                "user_name": user.username if user else None,
                "amount": "0.00"
            })

    return {
        "owe_to_me": owe_to_me_list,
        "i_owe_to": i_owe_to_list
    }

app.include_router(prefix_router)



# Run the server when file is executed
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # Makes server accessible externally
        port=8000,
        reload=True  # Auto-reload on code changes
    )