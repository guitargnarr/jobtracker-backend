"""
Gmail Scanner for Job Tracker
IMAP-based email scanning for job applications
"""

import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
import os
import re
import logging
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)

GMAIL_EMAIL = os.getenv("GMAIL_EMAIL", "matthewdscott7@gmail.com")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "wdfj euvs dqmn deak")


class GmailScanner:
    """Scan Gmail for job application responses"""

    def __init__(self, email_address: str = GMAIL_EMAIL, app_password: str = GMAIL_APP_PASSWORD):
        self.email_address = email_address
        self.app_password = app_password
        self.mail = None

    def connect(self) -> bool:
        """Connect to Gmail via IMAP"""
        try:
            self.mail = imaplib.IMAP4_SSL('imap.gmail.com')
            self.mail.login(self.email_address, self.app_password)
            logger.info(f"Connected to Gmail: {self.email_address}")
            return True
        except Exception as e:
            logger.error(f"Gmail connection failed: {e}")
            return False

    def disconnect(self):
        """Close Gmail connection"""
        if self.mail:
            try:
                self.mail.close()
                self.mail.logout()
            except Exception:
                pass

    def scan_emails(self, days: int = 14) -> Tuple[List[Dict], List[str]]:
        """
        Scan emails for job applications
        Returns: (list of applications, list of errors)
        """
        applications = []
        errors = []

        if not self.connect():
            errors.append("Failed to connect to Gmail")
            return applications, errors

        try:
            # Select All Mail folder
            self.mail.select('"[Gmail]/All Mail"')

            # Search last N days
            date_since = (datetime.now() - timedelta(days=days)).strftime('%d-%b-%Y')
            _, message_ids = self.mail.search(None, f'SINCE {date_since}')

            if not message_ids[0]:
                logger.info("No emails found in date range")
                return applications, errors

            email_ids = message_ids[0].split()
            logger.info(f"Found {len(email_ids)} emails to scan")

            # Scan each email
            for msg_id in email_ids[:100]:  # Limit to 100 most recent
                try:
                    app = self._parse_email(msg_id)
                    if app:
                        applications.append(app)
                except Exception as e:
                    errors.append(f"Error parsing email {msg_id}: {str(e)}")

            logger.info(f"Parsed {len(applications)} job applications")

        except Exception as e:
            logger.error(f"Error scanning emails: {e}")
            errors.append(str(e))

        finally:
            self.disconnect()

        return applications, errors

    def _parse_email(self, msg_id: bytes) -> Dict | None:
        """Parse single email for job application data"""
        try:
            _, msg_data = self.mail.fetch(msg_id, '(RFC822)')
            email_body = msg_data[0][1]
            message = email.message_from_bytes(email_body)

            # Decode subject
            subject = self._decode_header(message["Subject"])
            from_header = message.get("From", "")
            date_header = message.get("Date", "")

            # Get email body
            body = self._extract_body(message)

            # Check if job-related
            if not self._is_job_related(subject, body):
                return None

            # Skip noise (newsletters, alerts)
            if self._is_noise(from_header, subject):
                return None

            # Extract application data
            company = self._extract_company(from_header, subject, body)
            position = self._extract_position(subject, body)
            status = self._determine_status(subject, body)
            date_applied = self._parse_date(date_header)

            # Skip if can't extract key fields
            if company == "UNKNOWN" or position == "UNKNOWN POSITION":
                return None

            return {
                'Date_Applied': date_applied,
                'Company': company,
                'Position_Title': position,
                'Status': status,
                'Source': 'Email',
                'Response_Date': date_applied if status != 'Application_Sent' else '',
                'Notes': f'Detected from email: {subject[:100]}',
            }

        except Exception as e:
            logger.debug(f"Could not parse email: {e}")
            return None

    def _decode_header(self, header_value):
        """Decode email header"""
        if not header_value:
            return ""

        decoded = decode_header(header_value)[0]
        if isinstance(decoded[0], bytes):
            try:
                return decoded[0].decode(decoded[1] or 'utf-8', errors='replace')
            except Exception:
                return str(decoded[0])
        return decoded[0] or ""

    def _extract_body(self, message) -> str:
        """Extract email body text"""
        body = ""
        if message.is_multipart():
            for part in message.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body = payload.decode('utf-8', errors='replace')
                            break
                    except Exception:
                        pass
        else:
            try:
                payload = message.get_payload(decode=True)
                if payload:
                    body = payload.decode('utf-8', errors='replace')
            except Exception:
                pass

        return body[:2000]  # Limit to first 2000 chars

    def _is_job_related(self, subject: str, body: str) -> bool:
        """Check if email is job-related"""
        keywords = [
            'application', 'position', 'job', 'interview',
            'resume', 'career', 'opportunity', 'assessment',
            'thank you for applying', 'received your application'
        ]

        text = (subject + body).lower()
        return any(keyword in text for keyword in keywords)

    def _is_noise(self, from_header: str, subject: str) -> bool:
        """Filter out newsletters and non-application emails"""
        noise_patterns = [
            'newsletter', 'digest', 'job alert', 'job match',
            'recommended for you', 'similar jobs', 'career tips',
            'brightalk.com', 'godaddy.com', 'indeed.com/career',
            'monster.com/notifications'
        ]

        text = (from_header + subject).lower()
        return any(pattern in text for pattern in noise_patterns)

    def _extract_company(self, from_header: str, subject: str, body: str) -> str:
        """Extract company name"""
        # Try from subject line
        patterns = [
            r'application (?:was sent to|to) ([^-,\n.!]+)',
            r'from ([A-Z][a-zA-Z\s&]+) (?:<|$)',
            r'thank you for applying to ([^,\n.!]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, subject + body, re.IGNORECASE)
            if match:
                company = match.group(1).strip()
                if len(company) > 2 and company.lower() != 'unknown':
                    return company

        # Try from email domain
        domain_match = re.search(r'@([^>.\s]+)', from_header)
        if domain_match:
            domain = domain_match.group(1).title()
            # Skip generic domains
            if domain.lower() not in ['linkedin', 'indeed', 'workday', 'greenhouse', 'gmail']:
                return domain

        return "UNKNOWN"

    def _extract_position(self, subject: str, body: str) -> str:
        """Extract position title"""
        patterns = [
            r'application (?:received for|for) (?:the )?([^,\n.!]+?) (?:role|position)',
            r'(?:position|role):\s*([^\n,]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, subject + body, re.IGNORECASE)
            if match:
                position = match.group(1).strip()
                if len(position) > 3:
                    return position

        return "UNKNOWN POSITION"

    def _determine_status(self, subject: str, body: str) -> str:
        """Determine application status from email content"""
        text = (subject + body).lower()

        if 'interview' in text or 'phone screen' in text:
            return 'Interview_Invitation'
        elif 'unfortunately' in text or 'not selected' in text:
            return 'Rejected'
        elif 'assessment' in text or 'test' in text:
            return 'Assessment_Required'
        elif 'thank you for applying' in text or 'received your application' in text:
            return 'Application_Acknowledged'
        else:
            return 'Application_Sent'

    def _parse_date(self, date_header: str) -> str:
        """Parse email date to YYYY-MM-DD format"""
        try:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(date_header)
            return dt.strftime('%Y-%m-%d')
        except Exception:
            return datetime.now().strftime('%Y-%m-%d')
