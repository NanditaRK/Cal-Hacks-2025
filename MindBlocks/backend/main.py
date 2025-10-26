from typing import Annotated, Union
from fastapi import FastAPI, Depends, HTTPException, Cookie, status, UploadFile, File
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from pydantic import BaseModel
import os
import jwt
import httpx
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from dateutil import parser

from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
load_dotenv()

from llm_scheduler import plan_schedule



from agent import run_agent_on_syllabus, heuristically_extract_items
from pdf_extract import extract_text_from_pdf_bytes
from planner import compute_free_slots, allocate_study_blocks


# --- Config ---
SECRET_KEY = os.getenv("APP_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 10
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

# --- FastAPI App ---
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://mindblocks.vercel.app"],
    allow_credentials=True,  # ⚠️ must be True to allow cookies
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- OAuth Setup ---
oauth = OAuth()
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile https://www.googleapis.com/auth/calendar.events'
    }
)

# --- Models ---
class User(BaseModel):
    email: str
    full_name: Union[str, None] = None
    given_name: Union[str, None] = None
    family_name: Union[str, None] = None
    picture: Union[str, None] = None
    locale: Union[str, None] = None
    verified_email: Union[bool, None] = None
    disabled: Union[bool, None] = False  # For future password auth

class UserModel(User):
    hashed_password: str  # For password auth only

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None

# --- JWT Utility ---
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_session(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")
    return payload



@app.get("/")
def ping_server():
    return {"message": "AI Study Planner Backend is running"}

@app.get("/auth/google")
async def login_via_google(request: Request):
    redirect_uri = request.url_for('auth_via_google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/google/callback")
async def auth_via_google_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")
    if not user_info:
        raise HTTPException(status_code=400, detail="Failed to retrieve user info")

    payload = {
        "email": user_info.get("email"),
        "full_name": user_info.get("name"),
        "given_name": user_info.get("given_name"),
        "family_name": user_info.get("family_name"),
        "picture": user_info.get("picture"),
        "locale": user_info.get("locale"),
        "verified_email": user_info.get("email_verified"),
        "google_access_token": token["access_token"],
    }

    access_token = create_access_token(payload, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    response = RedirectResponse(url="https://mindblocks.vercel.app/dashboard")
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,  # True in production
        samesite="None"
    )
    return response

@app.get("/auth/logout")
async def logout():
    response = JSONResponse(content={"detail": "Logged out"})
    response.delete_cookie(
        key="access_token",
        path="/",
        samesite="None",  # must match set_cookie
        secure=True      # True in prod HTTPS
    )
    return response


@app.get("/me")
async def get_current_user_info(session: dict = Depends(get_current_session)):
    return {
        "authenticated": True,
        "user": User(**session)  # map JWT payload to User model
    }

@app.get("/calendar/events")
async def get_calendar_events(session: dict = Depends(get_current_session)):
    google_token = session.get("google_access_token")
    if not google_token:
        raise HTTPException(status_code=401, detail="Missing Google access token")

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://www.googleapis.com/calendar/v3/calendars/primary/events",
            headers={"Authorization": f"Bearer {google_token}"}
        )
        if resp.status_code != 200:
            return {"events": []}
        events_data = resp.json().get("items", [])
        # map to simplified format
        events = [
            {
                "summary": e.get("summary"),
                "start": e.get("start"),
                "end": e.get("end"),
            }
            for e in events_data
        ]
        
        return filter_calendar_events(events)


def filter_calendar_events(events):
    now = datetime.now(timezone.utc)  # current UTC time
    filtered_events = []  # <-- list, not dict

    for e in events:
        start_str = e.get("start", {}).get("dateTime")
        if start_str:
            start_dt = parser.isoparse(start_str)  # parse with timezone
            if start_dt > now:
                filtered_events.append(e)
    

    print(filtered_events)
    return {"events": filtered_events}


#  optional passwrd based auth (for future implementation) 

# Notes:
# - Depends on JWT creation function (`create_access_token`) and password hashing
# - Currently, the system is stateless via Google JWT session

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2schema = OAuth2PasswordBearer(tokenUrl='token')

# Fake DB for testing password auth
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}

def verify_password(plain_password, hashed_password):
    return password_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return password_context.hash(password)

def get_user_from_db(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserModel(**user_dict)

def authenticate(db, username: str, password: str):
    user = get_user_from_db(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    """
    optional password auth:
    - uses create_access_token (shared JWT function)
    - Compatible with Token/TokenData models
    """
    user = authenticate(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return Token(access_token=access_token, token_type="bearer")


# ----------------------------
# New endpoints for syllabus / study plan
# ----------------------------

@app.post("/upload/syllabus")
async def upload_syllabus(file: UploadFile = File(...)):
    """
    Upload a PDF syllabus file.
    Returns a snippet of the text and extracted items.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDFs supported")
    contents = await file.read()
    text = extract_text_from_pdf_bytes(contents)
    heuristic_items = heuristically_extract_items(text)
    return {"text_snippet": text[:1000], "heuristic_items": heuristic_items}


from fastapi import UploadFile, File, Depends, HTTPException
from pdf_extract import extract_text_from_pdf_bytes
from agent import run_agent_on_syllabus
from llm_scheduler import plan_schedule
from main import get_current_session  # your JWT cookie session
import httpx

@app.post("/schedule/generate")
async def generate_schedule(file: UploadFile = File(...), session: dict = Depends(get_current_session)):
    """
    Upload a syllabus PDF, parse it, and generate an LLM-based study schedule.
    Returns a JSON schedule of study blocks with start/end times and topics.
    """
    if not file:
        raise HTTPException(status_code=400, detail="No PDF file uploaded")

    file_bytes = await file.read()

    raw_text = extract_text_from_pdf_bytes(file_bytes)

    syllabus_items = run_agent_on_syllabus(raw_text)

    google_token = session.get("google_access_token")
    if not google_token:
        raise HTTPException(status_code=401, detail="Missing Google access token")

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://www.googleapis.com/calendar/v3/calendars/primary/events",
            headers={"Authorization": f"Bearer {google_token}"}
        )
        if resp.status_code != 200:
            existing_events = []
        else:
            existing_events = resp.json().get("items", [])

    schedule = plan_schedule(syllabus_items, existing_events)
    
     # debug
    # print("=== Generated Schedule ===")
    # for block in schedule:
    #     print(block)
    # print("==========================")

    return {"planned_events": schedule}


@app.post("/schedule/create")
async def create_schedule(payload: dict, session: dict = Depends(get_current_session)):  
    """
    Create the planned study blocks as events in Google Calendar.
    Payload example:
    {
        "planned_events": [
            {"title": "...", "description": "...", "start": "...", "end": "...", "topics": ["..."]}
        ]
    }
    """
    google_token = session.get("google_access_token")
    if not google_token:
        raise HTTPException(status_code=401, detail="Missing Google access token")
    planned = payload.get("planned_events", [])
    if not planned:
        raise HTTPException(status_code=400, detail="No events to create")

    created = []
    if google_token:
        print("google token is here")
        async with httpx.AsyncClient() as client:
            print(planned)
            for ev in planned:
                # need to edit to enhance the naming of the events later
                body = {
                    "summary": ev.get("title", "Work Block"),
                    "description": ev.get("topics", "General Study Session"),
                    "start": {"dateTime": ev["start"]},
                    "end": {"dateTime": ev["end"]}
                }
                print(body)
                resp = await client.post(
                    "https://www.googleapis.com/calendar/v3/calendars/primary/events",
                    headers={"Authorization": f"Bearer {google_token}"},
                    json=body
                )
                if resp.status_code in (200, 201):
                    created.append(resp.json())
                    
                print(created)
                print(resp.status_code)
    
        
    return {"created_count": len(created), "created": created}
