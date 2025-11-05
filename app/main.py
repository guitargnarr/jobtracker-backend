"""
Job Tracker API - "Synergy Dashboard™ 3000"
FastAPI backend for job application tracking
Matthew Scott - Louisville AI Consultant
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import logging

from .models import (
    Application, ApplicationCreate, ApplicationUpdate,
    GmailScanResult, DashboardStats, AuthMode, AuthStatus
)
from .csv_handler import CSVHandler
from .gmail_scanner import GmailScanner
from .mock_data import MockDataGenerator
from .auth import auth_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Job Tracker API - Synergy Dashboard™ 3000",
    description="Enterprise-grade job application tracking with AI-powered insights",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS - allow all origins for demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize handlers
csv_handler = CSVHandler()
gmail_scanner = GmailScanner()


# ============================================================================
# ROOT & HEALTH
# ============================================================================

@app.get("/")
def root() -> dict:
    """API information - with corporate humor"""
    return {
        "name": "Synergy Dashboard™ 3000",
        "tagline": "Leveraging paradigm shifts in job search optimization",
        "version": "3.0.0",
        "consultant": "Matthew Scott - Louisville AI Consultant",
        "features": {
            "synergy_score": "Proprietary algorithm for measuring career momentum",
            "ai_powered": "100% buzzword compliant",
            "cloud_native": "Runs on the most advanced distributed systems (your laptop)",
            "blockchain_ready": "Just kidding, but we could add that"
        },
        "endpoints": {
            "applications": "/api/applications",
            "stats": "/api/stats/overview",
            "gmail": "/api/gmail/scan",
            "auth": "/api/auth/mode"
        },
        "portfolio": "https://jaspermatters.com",
        "github": "https://github.com/guitargnarr"
    }


@app.get("/health")
def health_check() -> dict:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "3.0.0",
        "mode": auth_manager.get_mode(),
        "message": "All systems operational. Synergy levels optimal."
    }


# ============================================================================
# AUTHENTICATION
# ============================================================================

@app.post("/api/auth/mode", response_model=AuthStatus)
async def set_auth_mode(mode: AuthMode):
    """Toggle between demo and real mode"""
    if auth_manager.set_mode(mode.mode):
        logger.info(f"Switched to {mode.mode} mode")
        return auth_manager.get_status()
    else:
        raise HTTPException(status_code=400, detail="Invalid mode. Use 'demo' or 'real'")


@app.get("/api/auth/status", response_model=AuthStatus)
async def get_auth_status():
    """Get current authentication mode"""
    return auth_manager.get_status()


# ============================================================================
# APPLICATIONS CRUD
# ============================================================================

@app.get("/api/applications", response_model=List[Application])
async def get_applications(
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    source: Optional[str] = Query(None, description="Filter by source"),
    company: Optional[str] = Query(None, description="Filter by company"),
):
    """Get all applications with optional filters"""
    try:
        if auth_manager.is_demo():
            # Demo mode: return fake data
            applications = MockDataGenerator.generate_applications(50)
        else:
            # Real mode: query CSV
            if any([status, priority, source, company]):
                applications = csv_handler.filter_applications(
                    status=status,
                    priority=priority,
                    source=source,
                    company=company
                )
            else:
                applications = csv_handler.get_all_applications()

        logger.info(f"Returned {len(applications)} applications (mode: {auth_manager.get_mode()})")
        return applications

    except Exception as e:
        logger.error(f"Error fetching applications: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/applications/{app_id}", response_model=Application)
async def get_application(app_id: int):
    """Get single application by ID (row index)"""
    try:
        if auth_manager.is_demo():
            applications = MockDataGenerator.generate_applications(50)
            if 0 <= app_id < len(applications):
                return applications[app_id]
            raise HTTPException(status_code=404, detail="Application not found")

        application = csv_handler.get_application_by_index(app_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        return application

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching application: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/applications", response_model=dict)
async def create_application(application: ApplicationCreate):
    """Create new application"""
    try:
        if auth_manager.is_demo():
            return {
                "success": True,
                "message": "Demo mode: Application not actually saved",
                "id": 999
            }

        # Convert to dict
        app_dict = application.dict()

        # Add to CSV
        success = csv_handler.add_application(app_dict)

        if success:
            return {"success": True, "message": "Application created successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to create application")

    except Exception as e:
        logger.error(f"Error creating application: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/applications/{app_id}", response_model=dict)
async def update_application(app_id: int, updates: ApplicationUpdate):
    """Update existing application"""
    try:
        if auth_manager.is_demo():
            return {
                "success": True,
                "message": "Demo mode: Application not actually updated"
            }

        # Convert to dict, filter out None values
        update_dict = {k: v for k, v in updates.dict().items() if v is not None}

        success = csv_handler.update_application(app_id, update_dict)

        if success:
            return {"success": True, "message": "Application updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Application not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating application: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/applications/{app_id}", response_model=dict)
async def delete_application(app_id: int):
    """Delete application"""
    try:
        if auth_manager.is_demo():
            return {
                "success": True,
                "message": "Demo mode: Application not actually deleted"
            }

        success = csv_handler.delete_application(app_id)

        if success:
            return {"success": True, "message": "Application deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Application not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting application: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# GMAIL INTEGRATION
# ============================================================================

@app.post("/api/gmail/scan", response_model=GmailScanResult)
async def scan_gmail(days: int = Query(14, description="Days to scan")):
    """Trigger Gmail scan for new applications"""
    try:
        if auth_manager.is_demo():
            # Demo mode: return fake scan result
            return GmailScanResult(
                success=True,
                scanned_count=47,
                new_applications=3,
                updated_applications=5,
                errors=[],
                message="Demo mode: Simulated scan found 3 new applications! 🎉"
            )

        # Real mode: actually scan Gmail
        logger.info(f"Starting Gmail scan (last {days} days)")
        applications, errors = gmail_scanner.scan_emails(days=days)

        # TODO: Merge with existing CSV (update logic needed)
        # For now, just return what we found

        return GmailScanResult(
            success=len(errors) == 0,
            scanned_count=len(applications) + len(errors),
            new_applications=len(applications),
            updated_applications=0,
            errors=errors,
            message=f"Found {len(applications)} job applications in Gmail"
        )

    except Exception as e:
        logger.error(f"Gmail scan error: {e}")
        return GmailScanResult(
            success=False,
            scanned_count=0,
            new_applications=0,
            updated_applications=0,
            errors=[str(e)],
            message="Gmail scan failed"
        )


@app.get("/api/gmail/status")
async def gmail_status():
    """Get Gmail scan status"""
    return {
        "last_scan": "2025-11-05 09:00:00",
        "next_scan": "2025-11-06 09:00:00",
        "auto_scan_enabled": True,
        "scan_interval_hours": 24,
        "message": "Auto-scan running daily at 9am EST"
    }


# ============================================================================
# ANALYTICS & STATS
# ============================================================================

@app.get("/api/stats/overview", response_model=DashboardStats)
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        if auth_manager.is_demo():
            # Demo mode: return fake stats
            mock_apps = MockDataGenerator.generate_applications(50)
            return DashboardStats(
                total_applications=51,
                response_rate=32.7,
                active_opportunities=23,
                phishing_blocked=1,
                recent_applications=mock_apps[:5],
                top_companies=[
                    {"company": "Synergy Solutions", "count": 5},
                    {"company": "Paradigm Shift Inc", "count": 4},
                    {"company": "Innovation Enablers", "count": 3},
                ]
            )

        # Real mode: calculate from CSV
        stats = csv_handler.get_stats()
        recent = csv_handler.get_recent_applications(5)

        return DashboardStats(
            total_applications=stats['total_applications'],
            response_rate=stats['response_rate'],
            active_opportunities=stats['active_opportunities'],
            phishing_blocked=stats['phishing_blocked'],
            recent_applications=recent,
            top_companies=stats['top_companies']
        )

    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats/timeline")
async def get_timeline(months: int = Query(6, description="Number of months to show")):
    """Get monthly application timeline"""
    try:
        if auth_manager.is_demo():
            # Demo mode: return fake timeline
            return {
                "labels": ["2025-06", "2025-07", "2025-08", "2025-09", "2025-10", "2025-11"],
                "applications": [5, 8, 12, 18, 25, 26],
                "responses": [1, 2, 4, 6, 8, 11]
            }

        # Real mode: calculate from CSV
        timeline = csv_handler.get_application_timeline(months=months)
        return timeline

    except Exception as e:
        logger.error(f"Error fetching timeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats/companies")
async def get_top_companies():
    """Get top companies by application count"""
    try:
        if auth_manager.is_demo():
            return [
                {"company": "Synergy Solutions", "applications": 5, "responses": 2},
                {"company": "Paradigm Shift Inc", "applications": 4, "responses": 1},
                {"company": "Innovation Enablers", "applications": 3, "responses": 0},
            ]

        stats = csv_handler.get_stats()
        return stats['top_companies']

    except Exception as e:
        logger.error(f"Error fetching companies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats/status-breakdown")
async def get_status_breakdown():
    """Get breakdown of applications by status"""
    try:
        if auth_manager.is_demo():
            # Demo mode: return fake status breakdown
            return [
                {"status": "Applied", "count": 28, "percentage": 54.9},
                {"status": "Interview Scheduled", "count": 8, "percentage": 15.7},
                {"status": "Rejected", "count": 10, "percentage": 19.6},
                {"status": "Offer Received", "count": 4, "percentage": 7.8},
                {"status": "PHISHING_BLOCKED", "count": 1, "percentage": 2.0}
            ]

        # Real mode: calculate from CSV
        breakdown = csv_handler.get_status_breakdown()
        return breakdown

    except Exception as e:
        logger.error(f"Error fetching status breakdown: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats/source-breakdown")
async def get_source_breakdown():
    """Get response rate breakdown by source"""
    try:
        if auth_manager.is_demo():
            # Demo mode: return fake source breakdown
            return [
                {"source": "LinkedIn", "applications": 25, "responses": 7, "response_rate": 28.0},
                {"source": "Company Website", "applications": 15, "responses": 6, "response_rate": 40.0},
                {"source": "Referral", "applications": 8, "responses": 5, "response_rate": 62.5},
                {"source": "Email", "applications": 3, "responses": 0, "response_rate": 0.0}
            ]

        # Real mode: calculate from CSV
        source_breakdown = csv_handler.get_source_breakdown()
        return source_breakdown

    except Exception as e:
        logger.error(f"Error fetching source breakdown: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PHISHING
# ============================================================================

@app.get("/api/phishing/alerts")
async def get_phishing_alerts():
    """Get phishing attempts"""
    try:
        if auth_manager.is_demo():
            return [{
                "company": "Totally Legit Corp (FAKE)",
                "email": "scam@fake-jobs.com",
                "pattern": "Instant interview scam",
                "blocked_date": "2025-11-05"
            }]

        # Get phishing entries from CSV
        phishing = csv_handler.filter_applications(status="PHISHING")
        return phishing

    except Exception as e:
        logger.error(f"Error fetching phishing alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
