"""
Mock Data Generator for Demo Mode
Generates realistic fake job applications
"""

from datetime import datetime, timedelta
import random


class MockDataGenerator:
    """Generate fake job application data"""

    COMPANIES = [
        "Synergy Solutions", "Paradigm Shift Inc", "Leverage Corp",
        "Strategic Dynamics", "Innovation Enablers", "Disruptive Tech",
        "Blue Ocean Ventures", "Agile Ninjas", "Cloud Warriors",
        "Data Wizards", "AI Overlords LLC", "Future Forward Inc"
    ]

    POSITIONS = [
        "Senior Synergy Architect", "Lead Paradigm Engineer",
        "Principal Strategy Optimizer", "VP of Disruption",
        "Director of Innovation Enablement", "Chief Leverage Officer",
        "Senior Rockstar Developer", "Ninja DevOps Engineer",
        "Wizard Data Scientist", "Guru ML Engineer"
    ]

    LOCATIONS = [
        "Louisville, KY (Remote)", "San Francisco, CA (Hybrid)",
        "New York, NY (Remote)", "Austin, TX (Hybrid)",
        "Chicago, IL (On-site)", "Seattle, WA (Remote)",
        "Denver, CO (Hybrid)", "Boston, MA (Remote)"
    ]

    STATUS_OPTIONS = [
        "Applied_LinkedIn", "Application_Viewed", "Resume_Downloaded",
        "Interview_Invitation", "Application_Acknowledged"
    ]

    PRIORITY_OPTIONS = ["HIGH", "MEDIUM", "LOW"]

    NOTES = [
        "Applied via LinkedIn Easy Apply - Strong culture fit",
        "Reached out to hiring manager on LinkedIn",
        "Company values align with career goals",
        "Salary range: $90K-$120K - negotiable",
        "Referred by colleague - high confidence",
        "Remote-first company - flexible hours",
        "Fast-growing startup - equity available"
    ]

    @staticmethod
    def generate_applications(count: int = 50):
        """Generate N fake applications"""
        applications = []

        for i in range(count):
            # Date within last 30 days
            days_ago = random.randint(0, 30)
            date_applied = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')

            # Random response date (30% chance)
            response_date = ""
            if random.random() < 0.3:
                response_days_ago = random.randint(0, days_ago)
                response_date = (datetime.now() - timedelta(days=response_days_ago)).strftime('%Y-%m-%d')

            app = {
                'Date_Applied': date_applied,
                'Company': random.choice(MockDataGenerator.COMPANIES),
                'Position_Title': random.choice(MockDataGenerator.POSITIONS),
                'Location': random.choice(MockDataGenerator.LOCATIONS),
                'Contact_Name': "",
                'Contact_Email': "",
                'Source': random.choice(["LinkedIn", "Company Website", "Referral"]),
                'Status': random.choice(MockDataGenerator.STATUS_OPTIONS),
                'Response_Date': response_date,
                'Next_Action': "Wait for response" if not response_date else "Follow up on status",
                'Priority': random.choice(MockDataGenerator.PRIORITY_OPTIONS),
                'Notes': random.choice(MockDataGenerator.NOTES),
            }

            applications.append(app)

        # Add a few phishing examples
        applications.append({
            'Date_Applied': datetime.now().strftime('%Y-%m-%d'),
            'Company': 'Totally Legit Corp (FAKE)',
            'Position_Title': 'Instant Interview Opportunity!!!',
            'Location': 'EMAIL PHISHING',
            'Contact_Name': '',
            'Contact_Email': 'scam@fake-jobs.com',
            'Source': 'EMAIL',
            'Status': '⚠️ PHISHING',
            'Response_Date': '',
            'Next_Action': '❌ DO NOT RESPOND - SCAM',
            'Priority': '⚠️ FRAUD',
            'Notes': '⚠️ CONFIRMED PHISHING - Fake instant interview email',
        })

        return applications
