# File: alerts.py
import logging
from typing import Dict, Optional

# Set up logging for this module
logger = logging.getLogger(__name__)

class CustomAlert:
    """Custom alert class for managing alerts."""
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message

class AlertManager:
    """Manager for custom alerts."""
    def __init__(self):
        self.alerts: Dict[str, CustomAlert] = {}

    def add_alert(self, name: str, message: str) -> None:
        """Add a new alert."""
        logger.info(f"Adding alert: {name}")
        self.alerts[name] = CustomAlert(name, message)

    def get_alert(self, name: str) -> Optional[CustomAlert]:
        """Get an alert by name."""
        return self.alerts.get(name)

    def remove_alert(self, name: str) -> None:
        """Remove an alert by name."""
        if name in self.alerts:
            logger.info(f"Removing alert: {name}")
            del self.alerts[name]

# Pre-load flight simulation-specific alerts
def setup_default_alerts(alert_manager: AlertManager):
    """Load the default flight simulation alerts."""
    try:
        # Flight Milestone Alerts
        alert_manager.add_alert("takeoff_alert", "Takeoff successful! Time to soar through the skies. Fasten your seatbelts, folks!")
        alert_manager.add_alert("landing_alert", "Smooth landing! All passengers may now disembark. Well done, Captain!")
        alert_manager.add_alert("altitude_alert", "You've reached cruising altitude. Time to sit back, relax, and enjoy the views.")

        # Emergency Situation Alerts
        alert_manager.add_alert("engine_failure", "Engine failure detected! Prepare for emergency landing procedures.")
        alert_manager.add_alert("turbulence_warning", "Turbulence ahead! Keep a steady hand on the controls. Buckle up, viewers!")
        alert_manager.add_alert("crash_alert", "Mayday, Mayday! We've lost control! The plane is going down! RIP flight.")

        # User-Triggered Fun Alerts
        alert_manager.add_alert("passenger_complaint", "A passenger has complained about the in-flight service! Maybe a smoother ride next time?")
        alert_manager.add_alert("beverage_service", "Flight attendants, please serve beverages to the passengers. What's your drink of choice?")
        alert_manager.add_alert("bird_strike", "Bird strike! Watch out for the geese! Quick, recover control of the plane!")

        # Stream Interaction Alerts
        alert_manager.add_alert("new_crew_member", "Welcome aboard, [username]! You've officially joined the flight crew!")
        alert_manager.add_alert("low_fuel", "Warning: Low fuel! Should we refuel or attempt a landing?")

        # Realism/Procedural Alerts
        alert_manager.add_alert("checklist_reminder", "Captain, have you completed your pre-flight checklist? It's important to ensure a safe flight.")
        alert_manager.add_alert("nav_update", "New waypoint detected. Adjust heading to stay on course.")

        # Fun/Community Engagement Alerts
        alert_manager.add_alert("safety_briefing", "Please direct your attention to the safety briefing card in the seat pocket in front of you.")
        alert_manager.add_alert("captains_log", "Captain's Log: [Current in-game date/time]. The flight is progressing smoothly, and the crew is in good spirits.")
        alert_manager.add_alert("plane_upgrade", "The airline has upgraded/downgraded your plane. Time to adjust your flight plan!")

        # Airport and Flight Plan Alerts
        alert_manager.add_alert("runway_clear", "Runway cleared for takeoff. All systems go, Captain!")
        alert_manager.add_alert("diversion_alert", "Flight diverted due to weather or mechanical failure! Set course for the nearest airport.")
    except Exception as e:
        logger.error(f"Error setting up default alerts: {e}", exc_info=True)