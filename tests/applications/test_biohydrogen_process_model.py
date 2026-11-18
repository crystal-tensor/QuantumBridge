from dataclasses import replace
import numpy as np
import pytest
from scripts.biohydrogen_process_model import Parameters,simulate


@pytest.mark.parametrize('duty',[1,.25,.02])
def test_charge_and_oxygen_budgets_close_even_for_short_pulses(duty):
    row=simulate(Parameters(duty=duty,duration=6))
    assert row['summary']['electron_balance_max_error']<1e-8
    assert row['summary']['oxygen_balance_max_error']<1e-8
    a=np.array(row['states'])
    assert np.min(a)>-1e-8
    assert np.max(a[:,0])<=1+1e-8
    assert np.max(a[:,2])<=1+1e-8
    assert np.all(np.diff(a[:,3])>=-1e-9)


def test_darkness_cannot_produce_hydrogen_from_empty_reservoir():
    assert simulate(Parameters(input_light=0,duration=3))['summary']['H2_equivalents']==0


def test_equal_incident_photon_budget_not_equal_absorbed_electrons():
    a=simulate(Parameters(duration=4))
    b=simulate(Parameters(duration=4,duty=.25))
    assert a['summary']['incident_light_integral']==b['summary']['incident_light_integral']
    assert abs(a['states'][-1][4]-b['states'][-1][4])>.01


def test_numerical_refinement_converges():
    p=Parameters(duration=4,duty=.25)
    coarse=simulate(p,dt=.05)['summary']['H2_equivalents']
    fine=simulate(p,dt=.025,rtol=1e-10,atol=1e-12)['summary']['H2_equivalents']
    assert abs(coarse-fine)<1e-6
