from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import jwt
import bcrypt

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# Create the main app without a prefix
app = FastAPI(title="SyncLogic Portal API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    full_name: str
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class Application(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    icon: str
    category: str  # "native" or "portal"
    url: Optional[str] = None
    is_active: bool = True

# Helper functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await db.users.find_one({"username": username})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return User(**user)

# Routes
@api_router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password
    )
    
    await db.users.insert_one(user.dict())
    return UserResponse(**user.dict())

@api_router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    user = await db.users.find_one({"username": user_credentials.username})
    if not user or not verify_password(user_credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user["username"]})
    user_response = UserResponse(**user)
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )

@api_router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse(**current_user.dict())

@api_router.get("/applications", response_model=List[Application])
async def get_applications(current_user: User = Depends(get_current_user)):
    # Mock data for applications
    mock_applications = [
        # Native secure applications
        Application(
            id="app1",
            name="WordPress",
            description="Plateforme de gestion de contenu",
            icon="🌐",
            category="native",
            url="https://wordpress.example.com"
        ),
        Application(
            id="app2",
            name="Odoo ERP",
            description="Système de gestion d'entreprise",
            icon="📊",
            category="native",
            url="https://odoo.example.com"
        ),
        Application(
            id="app3",
            name="Nextcloud",
            description="Stockage et collaboration cloud",
            icon="☁️",
            category="native",
            url="https://nextcloud.example.com"
        ),
        Application(
            id="app4",
            name="GitLab CE",
            description="Plateforme DevOps intégrée",
            icon="🔧",
            category="native",
            url="https://gitlab.example.com"
        ),
        Application(
            id="app5",
            name="Jira",
            description="Gestion de projets Agile",
            icon="📋",
            category="native",
            url="https://jira.example.com"
        ),
        Application(
            id="app6",
            name="Confluence",
            description="Espace de travail collaboratif",
            icon="📝",
            category="native",
            url="https://confluence.example.com"
        ),
        Application(
            id="app7",
            name="Mattermost",
            description="Communication d'équipe sécurisée",
            icon="💬",
            category="native",
            url="https://mattermost.example.com"
        ),
        Application(
            id="app8",
            name="Grafana",
            description="Monitoring et visualisation",
            icon="📈",
            category="native",
            url="https://grafana.example.com"
        ),
        # Portal secured applications
        Application(
            id="portal1",
            name="Analytics Pro",
            description="Analyse avancée des données",
            icon="📊",
            category="portal"
        ),
        Application(
            id="portal2",
            name="CRM Manager",
            description="Gestion de la relation client",
            icon="👥",
            category="portal"
        ),
        Application(
            id="portal3",
            name="Invoice System",
            description="Système de facturation",
            icon="💰",
            category="portal"
        ),
        Application(
            id="portal4",
            name="Document Hub",
            description="Centre de documentation",
            icon="📁",
            category="portal"
        ),
        Application(
            id="portal5",
            name="Task Tracker",
            description="Suivi des tâches et projets",
            icon="✅",
            category="portal"
        ),
        Application(
            id="portal6",
            name="Report Builder",
            description="Générateur de rapports",
            icon="📄",
            category="portal"
        ),
        Application(
            id="portal7",
            name="Security Center",
            description="Centre de sécurité",
            icon="🔐",
            category="portal"
        ),
        Application(
            id="portal8",
            name="API Gateway",
            description="Passerelle d'API",
            icon="🔗",
            category="portal"
        )
    ]
    
    return mock_applications

@api_router.post("/applications/{app_id}/access-token")
async def generate_access_token(app_id: str, current_user: User = Depends(get_current_user)):
    # For this MVP, we'll return a mock token
    mock_token = f"portal_token_{app_id}_{current_user.id}_{int(datetime.utcnow().timestamp())}"
    return {"access_token": mock_token, "app_id": app_id}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()