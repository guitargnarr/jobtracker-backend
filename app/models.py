"""
Pydantic Models for Job Tracker API
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class Application(BaseModel):
    """Single job application"""
    Date_Applied: str = Field(..., description="Application date (YYYY-MM-DD)")
    Company: str = Field(..., min_length=1, description="Company name")
    Position_Title: str = Field(..., min_length=1, description="Job title")
    Location: str = Field(default="", description="Location (City, State)")
    Contact_Name: str = Field(default="", description="Contact person name")
    Contact_Email: str = Field(default="", description="Contact email")
    Source: str = Field(default="LinkedIn", description="Application source")
    Status: str = Field(default="Applied_LinkedIn", description="Application status")
    Response_Date: str = Field(default="", description="Response date (YYYY-MM-DD)")
    Next_Action: str = Field(default="Wait for response", description="Next step")
    Priority: str = Field(default="MEDIUM", description="Priority level")
    Notes: str = Field(default="", description="Additional notes")


class ApplicationCreate(BaseModel):
    """Create new application (subset of fields)"""
    Company: str
    Position_Title: str
    Location: str = ""
    Source: str = "LinkedIn"
    Priority: str = "MEDIUM"
    Notes: str = ""


class ApplicationUpdate(BaseModel):
    """Update application (all fields optional)"""
    Company: Optional[str] = None
    Position_Title: Optional[str] = None
    Location: Optional[str] = None
    Contact_Name: Optional[str] = None
    Contact_Email: Optional[str] = None
    Source: Optional[str] = None
    Status: Optional[str] = None
    Response_Date: Optional[str] = None
    Next_Action: Optional[str] = None
    Priority: Optional[str] = None
    Notes: Optional[str] = None


class GmailScanResult(BaseModel):
    """Result from Gmail scan"""
    success: bool
    scanned_count: int
    new_applications: int
    updated_applications: int
    errors: List[str] = []
    message: str


class DashboardStats(BaseModel):
    """Dashboard statistics"""
    total_applications: int
    response_rate: float
    active_opportunities: int
    phishing_blocked: int
    recent_applications: List[Application]
    top_companies: List[dict]


class AuthMode(BaseModel):
    """Authentication mode"""
    mode: str = Field(..., description="demo or real")


class AuthStatus(BaseModel):
    """Current auth status"""
    mode: str
    is_demo: bool
    message: str
