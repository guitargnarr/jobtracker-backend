"""
Authentication Module
Handles Demo vs Real mode switching
"""

from typing import Dict


class AuthManager:
    """Manage demo vs real mode"""

    def __init__(self):
        self.mode = "demo"  # Default to demo mode for safety

    def set_mode(self, mode: str) -> bool:
        """Set authentication mode"""
        if mode in ["demo", "real"]:
            self.mode = mode
            return True
        return False

    def get_mode(self) -> str:
        """Get current mode"""
        return self.mode

    def is_demo(self) -> bool:
        """Check if in demo mode"""
        return self.mode == "demo"

    def get_status(self) -> Dict:
        """Get auth status"""
        return {
            "mode": self.mode,
            "is_demo": self.is_demo(),
            "message": "Demo mode - fake data" if self.is_demo() else "Real mode - actual CSV data"
        }


# Global auth manager instance
auth_manager = AuthManager()
