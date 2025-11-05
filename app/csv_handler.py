"""
CSV Handler for Job Tracker
Handles reading/writing to JOB_TRACKER_LIVE.csv
"""

import pandas as pd
import os
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

CSV_PATH = os.getenv("CSV_PATH", "../data/JOB_TRACKER_LIVE.csv")


class CSVHandler:
    """Handle CSV operations"""

    def __init__(self, csv_path: str = CSV_PATH):
        self.csv_path = csv_path
        self.columns = [
            'Date_Applied', 'Company', 'Position_Title', 'Location',
            'Contact_Name', 'Contact_Email', 'Source', 'Status',
            'Response_Date', 'Next_Action', 'Priority', 'Notes'
        ]

    def read_csv(self) -> pd.DataFrame:
        """Read CSV file and return DataFrame"""
        try:
            if not os.path.exists(self.csv_path):
                logger.warning(f"CSV not found at {self.csv_path}, creating empty")
                return pd.DataFrame(columns=self.columns)

            df = pd.read_csv(self.csv_path)

            # Ensure all columns exist
            for col in self.columns:
                if col not in df.columns:
                    df[col] = ""

            # Fill NaN values with empty string
            df = df.fillna("")

            logger.info(f"Loaded {len(df)} applications from CSV")
            return df

        except Exception as e:
            logger.error(f"Error reading CSV: {e}")
            return pd.DataFrame(columns=self.columns)

    def write_csv(self, df: pd.DataFrame) -> bool:
        """Write DataFrame to CSV"""
        try:
            # Backup existing file
            if os.path.exists(self.csv_path):
                backup_path = f"{self.csv_path}.backup"
                df_existing = pd.read_csv(self.csv_path)
                df_existing.to_csv(backup_path, index=False)

            # Write new data
            df[self.columns].to_csv(self.csv_path, index=False)
            logger.info(f"Wrote {len(df)} applications to CSV")
            return True

        except Exception as e:
            logger.error(f"Error writing CSV: {e}")
            return False

    def get_all_applications(self) -> List[Dict]:
        """Get all applications as list of dicts"""
        df = self.read_csv()
        return df.to_dict('records')

    def get_application_by_index(self, index: int) -> Optional[Dict]:
        """Get single application by row index"""
        df = self.read_csv()
        if 0 <= index < len(df):
            return df.iloc[index].to_dict()
        return None

    def add_application(self, application: Dict) -> bool:
        """Add new application"""
        try:
            df = self.read_csv()

            # Set Date_Applied to today if not provided
            if 'Date_Applied' not in application or not application['Date_Applied']:
                application['Date_Applied'] = datetime.now().strftime('%Y-%m-%d')

            # Create new row with all columns
            new_row = {col: application.get(col, "") for col in self.columns}

            # Append to DataFrame
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

            return self.write_csv(df)

        except Exception as e:
            logger.error(f"Error adding application: {e}")
            return False

    def update_application(self, index: int, updates: Dict) -> bool:
        """Update application by index"""
        try:
            df = self.read_csv()

            if not (0 <= index < len(df)):
                logger.error(f"Invalid index: {index}")
                return False

            # Update fields
            for key, value in updates.items():
                if key in df.columns and value is not None:
                    df.at[index, key] = value

            return self.write_csv(df)

        except Exception as e:
            logger.error(f"Error updating application: {e}")
            return False

    def delete_application(self, index: int) -> bool:
        """Delete application by index"""
        try:
            df = self.read_csv()

            if not (0 <= index < len(df)):
                logger.error(f"Invalid index: {index}")
                return False

            df = df.drop(index).reset_index(drop=True)
            return self.write_csv(df)

        except Exception as e:
            logger.error(f"Error deleting application: {e}")
            return False

    def get_stats(self) -> Dict:
        """Calculate dashboard statistics"""
        df = self.read_csv()

        if len(df) == 0:
            return {
                'total_applications': 0,
                'response_rate': 0.0,
                'active_opportunities': 0,
                'phishing_blocked': 0,
            }

        total = len(df)
        responded = len(df[df['Response_Date'] != ""])
        response_rate = (responded / total * 100) if total > 0 else 0.0

        # Active = Applied but no response yet
        active = len(df[
            (df['Status'].str.contains('Applied', na=False))
            & (df['Response_Date'] == "")
        ])

        # Phishing
        phishing = len(df[df['Status'].str.contains('PHISHING', na=False)])

        # Top companies
        company_counts = df['Company'].value_counts().head(10)
        top_companies = [
            {"company": company, "count": int(count)}
            for company, count in company_counts.items()
        ]

        return {
            'total_applications': total,
            'response_rate': round(response_rate, 1),
            'active_opportunities': active,
            'phishing_blocked': phishing,
            'top_companies': top_companies,
        }

    def get_recent_applications(self, limit: int = 10) -> List[Dict]:
        """Get most recent applications"""
        df = self.read_csv()

        # Sort by Date_Applied descending
        df_sorted = df.sort_values('Date_Applied', ascending=False)

        return df_sorted.head(limit).to_dict('records')

    def filter_applications(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        source: Optional[str] = None,
        company: Optional[str] = None,
    ) -> List[Dict]:
        """Filter applications by criteria"""
        df = self.read_csv()

        if status:
            df = df[df['Status'].str.contains(status, case=False, na=False)]

        if priority:
            df = df[df['Priority'] == priority]

        if source:
            df = df[df['Source'].str.contains(source, case=False, na=False)]

        if company:
            df = df[df['Company'].str.contains(company, case=False, na=False)]

        return df.to_dict('records')
