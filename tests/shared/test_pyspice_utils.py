import pytest
from PySpice.Unit import *
from shared.pyspice_utils import calculate_power_budget, create_circuit
from shared.models.schemas import PowerSupplyConfig, PowerBudgetResult

def test_calculate_power_budget_safe():
    circuit = create_circuit("test_safe")
    # Prefix with 'vsupply' as per pyspice_utils.py:68
    circuit.V("vsupply", "vcc", circuit.gnd, 24 @ u_V)
    circuit.R("load", "vcc", circuit.gnd, 12 @ u_Ohm) # 2A
    
    psu_config = PowerSupplyConfig(voltage_dc=24, max_current_a=10)
    
    result = calculate_power_budget(circuit, psu_config)
    
    assert isinstance(result, PowerBudgetResult)
    assert result.total_draw_a == 2.0
    assert result.psu_capacity_a == 10.0
    assert result.margin_a == 8.0
    assert result.margin_pct == 80.0
    assert result.is_safe is True
    assert result.errors == []

def test_calculate_power_budget_overcurrent():
    circuit = create_circuit("test_over")
    circuit.V("vsupply", "vcc", circuit.gnd, 24 @ u_V)
    circuit.R("load", "vcc", circuit.gnd, 2 @ u_Ohm) # 12A
    
    psu_config = PowerSupplyConfig(voltage_dc=24, max_current_a=10)
    
    result = calculate_power_budget(circuit, psu_config)
    
    assert result.total_draw_a == 12.0
    assert result.is_safe is False
    assert any("OVERCURRENT" in e for e in result.errors)

if __name__ == "__main__":
    # Simple runner if pytest not used
    try:
        test_calculate_power_budget_safe()
        print("test_calculate_power_budget_safe: PASSED")
        test_calculate_power_budget_overcurrent()
        print("test_calculate_power_budget_overcurrent: PASSED")
    except Exception as e:
        print(f"Tests failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
