"""
TimeService - MCP service for time-related functionality
"""

import logging
from typing import Dict, Any
from datetime import datetime
import locale
from pydantic import BaseModel
import ntplib

logger = logging.getLogger(__name__)


class MCPServiceBase:
    """Base class for MCP services"""

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(self.__class__.__name__)

    async def initialize(self):
        """Initialize the service"""
        pass

    async def shutdown(self):
        """Shutdown the service"""
        pass


class TimeResult(BaseModel):
    """Time result model"""

    timestamp: float
    formatted_time: str
    timezone: str = "UTC"
    status: str = "success"
    message: str = ""


class TimeService(MCPServiceBase):
    """
    MCP service for time-related operations using NTP
    """

    def __init__(
        self,
        ntp_server: str = "de.pool.ntp.org",
        ntp_version: int = 3,
        locale_setting: str = "de_DE.utf8",
    ):
        super().__init__(name="time_service")
        self.ntp_server = ntp_server
        self.ntp_version = ntp_version
        self.locale_setting = locale_setting
        self.client = ntplib.NTPClient()
        self.logger = logging.getLogger(self.__class__.__name__)

    async def initialize(self):
        """Initialize the time service"""
        self._set_locale()
        self.logger.info("TimeService initialized")

    def _set_locale(self):
        """Set system locale for time formatting"""
        try:
            locale.setlocale(locale.LC_TIME, self.locale_setting)
            self.logger.info(f"Locale set to {self.locale_setting}")
        except locale.Error as e:
            self.logger.error(f"Could not set locale to {self.locale_setting}: {e}")
            # Continue with default locale

    async def get_current_time(
        self, format_string: str = "%A, %d. %B %Y, %H:%M:%S"
    ) -> TimeResult:
        """
        Get current time from NTP server

        Args:
            format_string: strftime format string for time formatting

        Returns:
            TimeResult with current time information
        """
        try:
            self.logger.info(f"Fetching time from NTP server: {self.ntp_server}")

            response = self.client.request(self.ntp_server, version=self.ntp_version)
            dt = datetime.fromtimestamp(response.tx_time)

            # Ensure locale is set before formatting
            self._set_locale()
            formatted_time = dt.strftime(format_string)

            return TimeResult(
                timestamp=response.tx_time,
                formatted_time=formatted_time,
                timezone="NTP Server Time",
            )

        except ntplib.NTPException as e:
            self.logger.error(f"NTP error: {e}")
            return TimeResult(
                timestamp=0.0,
                formatted_time="",
                status="error",
                message=f"NTP error: {str(e)}",
            )
        except Exception as e:
            self.logger.error(f"Unexpected error getting time: {e}")
            return TimeResult(
                timestamp=0.0,
                formatted_time="",
                status="error",
                message=f"Time fetch failed: {str(e)}",
            )

    async def get_local_time(
        self, format_string: str = "%A, %d. %B %Y, %H:%M:%S"
    ) -> TimeResult:
        """
        Get current local system time

        Args:
            format_string: strftime format string for time formatting

        Returns:
            TimeResult with local time information
        """
        try:
            dt = datetime.now()
            self._set_locale()
            formatted_time = dt.strftime(format_string)

            return TimeResult(
                timestamp=dt.timestamp(),
                formatted_time=formatted_time,
                timezone="Local System Time",
            )

        except Exception as e:
            self.logger.error(f"Error getting local time: {e}")
            return TimeResult(
                timestamp=0.0,
                formatted_time="",
                status="error",
                message=f"Local time fetch failed: {str(e)}",
            )

    async def format_timestamp(
        self, timestamp: float, format_string: str = "%A, %d. %B %Y, %H:%M:%S"
    ) -> Dict[str, Any]:
        """
        Format a given timestamp

        Args:
            timestamp: Unix timestamp to format
            format_string: strftime format string

        Returns:
            Dictionary with formatted time information
        """
        try:
            dt = datetime.fromtimestamp(timestamp)
            self._set_locale()
            formatted_time = dt.strftime(format_string)

            return {
                "original_timestamp": timestamp,
                "formatted_time": formatted_time,
                "status": "success",
            }

        except Exception as e:
            self.logger.error(f"Error formatting timestamp {timestamp}: {e}")
            return {
                "original_timestamp": timestamp,
                "formatted_time": "",
                "status": "error",
                "message": str(e),
            }

    async def time_difference(
        self, timestamp1: float, timestamp2: float
    ) -> Dict[str, Any]:
        """
        Calculate time difference between two timestamps

        Args:
            timestamp1: First timestamp
            timestamp2: Second timestamp

        Returns:
            Dictionary with time difference information
        """
        try:
            diff_seconds = abs(timestamp2 - timestamp1)

            days = int(diff_seconds // 86400)
            hours = int((diff_seconds % 86400) // 3600)
            minutes = int((diff_seconds % 3600) // 60)
            seconds = int(diff_seconds % 60)

            return {
                "timestamp1": timestamp1,
                "timestamp2": timestamp2,
                "difference_seconds": diff_seconds,
                "formatted_difference": f"{days} Tage, {hours} Stunden, {minutes} Minuten, {seconds} Sekunden",
                "status": "success",
            }

        except Exception as e:
            self.logger.error(f"Error calculating time difference: {e}")
            return {
                "timestamp1": timestamp1,
                "timestamp2": timestamp2,
                "status": "error",
                "message": str(e),
            }

    async def shutdown(self):
        """Shutdown the time service"""
        self.logger.info("TimeService shutdown completed")
