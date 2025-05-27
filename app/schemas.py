from typing import Optional, TypedDict

class SessionInfo(TypedDict):
    session_id: Optional[str]
    status: Optional[str]
    origin: Optional[str]
    destination: Optional[str]
    date: Optional[str]
    airline: Optional[str]