"""Tests for electrical failure modes mapping."""

import pytest

from shared.electrical_failure_modes import (
    ElectricalFailureEvent,
    ElectricalFailureModeMapper,
)
from shared.enums import SimulationFailureMode


class TestElectricalFailureModeMapper:
    """Test the electrical failure modes mapper."""

    def test_map_short_circuit_event(self):
        """Test mapping of short circuit events."""
        event = ElectricalFailureEvent(
            event_type="short_circuit",
            component_id="R1",
        )
        result = ElectricalFailureModeMapper.map_event_to_failure_mode(event)
        assert result == SimulationFailureMode.SHORT_CIRCUIT

    def test_map_overcurrent_supply_event(self):
        """Test mapping of overcurrent supply events."""
        event = ElectricalFailureEvent(
            event_type="overcurrent_supply",
            details="Supply current 15A exceeds 10A limit",
        )
        result = ElectricalFailureModeMapper.map_event_to_failure_mode(event)
        assert result == SimulationFailureMode.OVERCURRENT_SUPPLY

    def test_map_wire_torn_event(self):
        """Test mapping of wire torn events."""
        event = ElectricalFailureEvent(
            event_type="wire_torn",
            component_id="W1",
            details="Tension 50N exceeds 40N AWG rating",
        )
        result = ElectricalFailureModeMapper.map_event_to_failure_mode(event)
        assert result == SimulationFailureMode.WIRE_TORN

    def test_map_open_circuit_event(self):
        """Test mapping of open circuit events."""
        event = ElectricalFailureEvent(
            event_type="open_circuit",
            details="Floating node detected at junction",
        )
        result = ElectricalFailureModeMapper.map_event_to_failure_mode(event)
        assert result == SimulationFailureMode.OPEN_CIRCUIT

    def test_map_overcurrent_wire_event(self):
        """Test mapping of overcurrent wire events."""
        event = ElectricalFailureEvent(
            event_type="overcurrent_wire",
            component_id="W2",
            details="Wire AWG 24 rated 3.5A, got 5A",
        )
        result = ElectricalFailureModeMapper.map_event_to_failure_mode(event)
        assert result == SimulationFailureMode.OVERCURRENT_WIRE

    def test_map_error_string_short_circuit(self):
        """Test mapping error strings for short circuits."""
        result = ElectricalFailureModeMapper.map_error_string_to_failure_mode(
            "FAILED_SHORT_CIRCUIT at node GND"
        )
        assert result == SimulationFailureMode.SHORT_CIRCUIT

    def test_map_error_string_overcurrent_supply(self):
        """Test mapping error strings for overcurrent supply."""
        result = ElectricalFailureModeMapper.map_error_string_to_failure_mode(
            "Error: FAILED_OVERCURRENT_SUPPLY - 15A > 10A"
        )
        assert result == SimulationFailureMode.OVERCURRENT_SUPPLY

    def test_map_error_string_wire_torn(self):
        """Test mapping error strings for wire torn."""
        result = ElectricalFailureModeMapper.map_error_string_to_failure_mode(
            "simulation_fail: wire_torn for wire_1"
        )
        assert result == SimulationFailureMode.WIRE_TORN

    def test_map_error_string_open_circuit(self):
        """Test mapping error strings for open circuits."""
        result = ElectricalFailureModeMapper.map_error_string_to_failure_mode(
            "Circuit validation failed: floating_node at node_5"
        )
        assert result == SimulationFailureMode.OPEN_CIRCUIT

    def test_case_insensitive_mapping(self):
        """Test that mapping is case-insensitive."""
        # Uppercase
        event_upper = ElectricalFailureEvent(event_type="SHORT_CIRCUIT")
        result_upper = ElectricalFailureModeMapper.map_event_to_failure_mode(
            event_upper
        )
        assert result_upper == SimulationFailureMode.SHORT_CIRCUIT

        # Mixed case
        event_mixed = ElectricalFailureEvent(event_type="Short_Circuit")
        result_mixed = ElectricalFailureModeMapper.map_event_to_failure_mode(
            event_mixed
        )
        assert result_mixed == SimulationFailureMode.SHORT_CIRCUIT

    def test_unknown_event_defaults_to_open_circuit(self):
        """Test that unknown events default to open circuit."""
        event = ElectricalFailureEvent(event_type="unknown_electrical_error")
        result = ElectricalFailureModeMapper.map_event_to_failure_mode(event)
        assert result == SimulationFailureMode.OPEN_CIRCUIT

    def test_get_all_electrical_failure_modes(self):
        """Test retrieving all electrical failure modes."""
        modes = ElectricalFailureModeMapper.get_all_electrical_failure_modes()
        assert len(modes) == 5
        assert SimulationFailureMode.SHORT_CIRCUIT in modes
        assert SimulationFailureMode.OVERCURRENT_SUPPLY in modes
        assert SimulationFailureMode.OVERCURRENT_WIRE in modes
        assert SimulationFailureMode.OPEN_CIRCUIT in modes
        assert SimulationFailureMode.WIRE_TORN in modes

    def test_is_electrical_failure(self):
        """Test electrical failure type checking."""
        assert ElectricalFailureModeMapper.is_electrical_failure(
            SimulationFailureMode.SHORT_CIRCUIT
        )
        assert ElectricalFailureModeMapper.is_electrical_failure(
            SimulationFailureMode.WIRE_TORN
        )
        assert not ElectricalFailureModeMapper.is_electrical_failure(
            SimulationFailureMode.TIMEOUT
        )
        assert not ElectricalFailureModeMapper.is_electrical_failure(None)

    def test_event_with_full_details(self):
        """Test event mapping with all detail fields."""
        event = ElectricalFailureEvent(
            event_type="short_circuit",
            component_id="SW1",
            severity="critical",
            details="Switch SW1 directly shorted across battery terminals",
        )
        result = ElectricalFailureModeMapper.map_event_to_failure_mode(event)
        assert result == SimulationFailureMode.SHORT_CIRCUIT
