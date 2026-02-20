# Electrical Failure Modes - Implementation Guide

## Overview

The electrical failure modes system maps simulation events and validation errors to standardized failure enums. This enables consistent failure detection and reporting across the system.

## Failure Modes Defined

The following electrical failure modes are defined in `shared.enums.SimulationFailureMode`:

| Enum Member | Value | Description |
|---|---|---|
| `SHORT_CIRCUIT` | `FAILED_SHORT_CIRCUIT` | Direct connection bypassing circuit elements (e.g., switch across battery) |
| `OVERCURRENT_SUPPLY` | `FAILED_OVERCURRENT_SUPPLY` | Total circuit draw exceeds power supply rating |
| `OVERCURRENT_WIRE` | `FAILED_OVERCURRENT_WIRE` | Current through wire exceeds AWG gauge rating |
| `OPEN_CIRCUIT` | `FAILED_OPEN_CIRCUIT` | Circuit disconnection or floating node detected |
| `WIRE_TORN` | `FAILED_WIRE_TORN` | Wire mechanical failure due to excess tension |

## Usage

### Mapping from Validation Errors

```python
from shared.electrical_failure_modes import ElectricalFailureModeMapper

# Map validation error string
mode = ElectricalFailureModeMapper.map_error_string_to_failure_mode(
    "FAILED_SHORT_CIRCUIT at node GND"
)
# mode == SimulationFailureMode.SHORT_CIRCUIT
```

### Mapping from Events

```python
from shared.electrical_failure_modes import (
    ElectricalFailureEvent,
    ElectricalFailureModeMapper,
)

# Create an electrical failure event
event = ElectricalFailureEvent(
    event_type="wire_torn",
    component_id="W1",
    severity="critical",
    details="Wire tension 50N exceeds 40N tensile strength limit"
)

# Map to failure mode enum
mode = ElectricalFailureModeMapper.map_event_to_failure_mode(event)
# mode == SimulationFailureMode.WIRE_TORN
```

### Checking if a Failure is Electrical

```python
from shared.electrical_failure_modes import ElectricalFailureModeMapper

if ElectricalFailureModeMapper.is_electrical_failure(failure_mode):
    # Handle electrical failure
    print(f"Electrical failure detected: {failure_mode}")
```

### Getting All Electrical Failure Modes

```python
modes = ElectricalFailureModeMapper.get_all_electrical_failure_modes()
# Returns list of all 5 electrical failure modes
```

## Integration Points

### Circuit Validation

When performing PySpice circuit validation, capture failures as events:

```python
from shared.pyspice_utils import validate_circuit
from shared.electrical_failure_modes import (
    ElectricalFailureEvent,
    ElectricalFailureModeMapper,
)

result = validate_circuit(circuit)
if not result.valid:
    for error in result.errors:
        event = ElectricalFailureEvent(
            event_type="validation_error",
            details=error
        )
        failure_mode = ElectricalFailureModeMapper.map_event_to_failure_mode(event)
```

### Simulation Physics Loop

When detecting failures during physics simulation:

```python
from shared.electrical_failure_modes import (
    ElectricalFailureEvent,
    ElectricalFailureModeMapper,
)
from shared.enums import SimulationFailureMode

if tension > wire_limit:
    event = ElectricalFailureEvent(
        event_type="wire_torn",
        component_id=wire.wire_id,
        details=f"Tension {tension:.2f}N exceeds {limit:.2f}N limit"
    )
    failure_mode = ElectricalFailureModeMapper.map_event_to_failure_mode(event)
    self.fail_reason = failure_mode
```

### Observability Events

The `ElectricalFailureEvent` can be emitted for observability:

```python
from shared.observability.events import emit_event
from shared.observability.schemas import ElectricalFailureEvent as ObservedEvent

emit_event(
    ObservedEvent(
        failure_type="short_circuit",
        component_id="SW1",
        message="Switch directly shorted battery terminals"
    )
)
```

## Testing

Comprehensive tests are provided in `tests/shared/test_electrical_failure_modes.py`:

```bash
pytest tests/shared/test_electrical_failure_modes.py -v
```

Tests cover:
- Event-to-mode mapping
- Error string parsing
- Case-insensitive matching
- Electrical failure detection
- Default behavior for unknown failures

## Event Type Keywords

The mapper recognizes these event type keywords (case-insensitive):

- `short_circuit`, `SHORT_CIRCUIT`, `FAILED_SHORT_CIRCUIT`
- `overcurrent_supply`, `FAILED_OVERCURRENT_SUPPLY`
- `overcurrent_wire`, `FAILED_OVERCURRENT_WIRE`
- `open_circuit`, `floating_node`, `FAILED_OPEN_CIRCUIT`
- `wire_torn`, `FAILED_WIRE_TORN`

## Default Behavior

Unknown electrical failure events default to `FAILED_OPEN_CIRCUIT` as the most conservative assumption (no connectivity).

## Related Components

- **Circuit Validation**: `shared.pyspice_utils.validate_circuit()`
- **Simulation Loop**: `worker_heavy.simulation.loop.SimulationLoop`
- **Enums**: `shared.enums.SimulationFailureMode`
- **Observability**: `shared.observability.schemas.ElectricalFailureEvent`
