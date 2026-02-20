"""
Electrical Failure Modes Mapping

Maps simulation events and validation errors to electrical failure enums.
Provides a central location for electrical failure detection and classification.
"""

from enum import StrEnum
from typing import NamedTuple

from shared.enums import SimulationFailureMode


class ElectricalFailureEvent(NamedTuple):
    """Represents an electrical failure event."""
    
    event_type: str  # e.g., "short_circuit", "wire_torn", "overcurrent"
    component_id: str | None = None
    severity: str = "critical"  # critical, warning
    details: str = ""


class ElectricalFailureModeMapper:
    """Maps simulation events and validation errors to electrical failure enums."""

    # Mapping from error messages / event types to failure modes
    FAILURE_MODE_MAP = {
        # Short circuit detection
        "short_circuit": SimulationFailureMode.SHORT_CIRCUIT,
        "failed_short_circuit": SimulationFailureMode.SHORT_CIRCUIT,
        "SHORT_CIRCUIT": SimulationFailureMode.SHORT_CIRCUIT,
        
        # Overcurrent supply (PSU limit exceeded)
        "overcurrent_supply": SimulationFailureMode.OVERCURRENT_SUPPLY,
        "overcurrent": SimulationFailureMode.OVERCURRENT_SUPPLY,
        "failed_overcurrent_supply": SimulationFailureMode.OVERCURRENT_SUPPLY,
        "FAILED_OVERCURRENT_SUPPLY": SimulationFailureMode.OVERCURRENT_SUPPLY,
        
        # Overcurrent in wire (AWG rating exceeded)
        "overcurrent_wire": SimulationFailureMode.OVERCURRENT_WIRE,
        "failed_overcurrent_wire": SimulationFailureMode.OVERCURRENT_WIRE,
        "FAILED_OVERCURRENT_WIRE": SimulationFailureMode.OVERCURRENT_WIRE,
        
        # Open circuit (floating node, disconnection)
        "open_circuit": SimulationFailureMode.OPEN_CIRCUIT,
        "floating_node": SimulationFailureMode.OPEN_CIRCUIT,
        "failed_open_circuit": SimulationFailureMode.OPEN_CIRCUIT,
        "FAILED_OPEN_CIRCUIT": SimulationFailureMode.OPEN_CIRCUIT,
        
        # Wire torn (tension exceeded)
        "wire_torn": SimulationFailureMode.WIRE_TORN,
        "failed_wire_torn": SimulationFailureMode.WIRE_TORN,
        "FAILED_WIRE_TORN": SimulationFailureMode.WIRE_TORN,
    }

    @classmethod
    def map_event_to_failure_mode(
        cls, event: ElectricalFailureEvent
    ) -> SimulationFailureMode:
        """
        Map an electrical failure event to a SimulationFailureMode enum.
        
        Args:
            event: The electrical failure event
            
        Returns:
            The corresponding SimulationFailureMode enum value
        """
        # Try exact match on event_type
        if event.event_type in cls.FAILURE_MODE_MAP:
            return cls.FAILURE_MODE_MAP[event.event_type]
        
        # Try case-insensitive match
        lower_type = event.event_type.lower()
        if lower_type in cls.FAILURE_MODE_MAP:
            return cls.FAILURE_MODE_MAP[lower_type]
        
        # Try substring match
        for key, mode in cls.FAILURE_MODE_MAP.items():
            if key.lower() in lower_type or lower_type in key.lower():
                return mode
        
        # Default to OPEN_CIRCUIT if unknown
        return SimulationFailureMode.OPEN_CIRCUIT

    @classmethod
    def map_error_string_to_failure_mode(
        cls, error_string: str
    ) -> SimulationFailureMode:
        """
        Map an error string from validation to a SimulationFailureMode enum.
        
        Args:
            error_string: The error message from circuit validation
            
        Returns:
            The corresponding SimulationFailureMode enum value
        """
        # Check for each failure type in the error string
        error_lower = error_string.lower()
        
        for key, mode in cls.FAILURE_MODE_MAP.items():
            if key.lower() in error_lower:
                return mode
        
        # Default to OPEN_CIRCUIT for unknown electrical errors
        return SimulationFailureMode.OPEN_CIRCUIT

    @classmethod
    def get_all_electrical_failure_modes(cls) -> list[SimulationFailureMode]:
        """Get all electrical failure modes."""
        return [
            SimulationFailureMode.SHORT_CIRCUIT,
            SimulationFailureMode.OVERCURRENT_SUPPLY,
            SimulationFailureMode.OVERCURRENT_WIRE,
            SimulationFailureMode.OPEN_CIRCUIT,
            SimulationFailureMode.WIRE_TORN,
        ]

    @classmethod
    def is_electrical_failure(
        cls, failure_mode: SimulationFailureMode | None
    ) -> bool:
        """Check if a failure mode is an electrical failure."""
        if failure_mode is None:
            return False
        return failure_mode in cls.get_all_electrical_failure_modes()
