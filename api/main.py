import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- 1. SETUP PATHS ---
# This line tells Python: "Look for imports in the folder above this one"
# It allows us to import from 'ai_engine' without moving files.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ai_engine.orchestrator import Orchestrator
    # If you have specific models, import them here too
    # from ai_engine.models.user_state import UserState
except ImportError as e:
    print(f"❌ Error importing ai_engine: {e}")
    print("Make sure you run this from the root 'FigureIt' folder!")
    sys.exit(1)

# --- 2. INITIALIZE APP ---
app = FastAPI()
orchestrator = Orchestrator()

# Allow your React Frontend (web_app) to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- 3. DEFINE INPUT FORMATS ---
class ContextRequest(BaseModel):
    user_id: str
    college_tier: str
    year_of_study: str
    hours_per_week: int


# --- 4. API ENDPOINTS ---

@app.get("/")
def health_check():
    return {"status": "FigureIt Backend is Online 🟢"}


@app.post("/start-session")
def start_session(data: ContextRequest):
    # This calls your existing orchestrator logic
    try:
        # Assuming your Orchestrator has a create_user method
        # If not, you might need to adjust this line to match your code
        # result = orchestrator.create_user(data.user_id, data)

        # For now, let's just test the connection:
        return {"status": "Session Started", "user_id": data.user_id, "message": "Connected to Orchestrator"}
    except Exception as e:
        return {"error": str(e)}

# Add more endpoints here as you build them...