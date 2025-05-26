from pydantic import BaseModel
from typing import Optional

class SessionInfo(BaseModel):
    session_id: Optional[str]
    status: Optional[str]
    origin: Optional[str]
    destination: Optional[str]
    date: Optional[str]
    airline: Optional[str]