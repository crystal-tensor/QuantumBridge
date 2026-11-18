"""Independent mathematical checks for the patent's explicitly separated readings."""
import numpy as np
import pytest
from scripts.biohydrogen_patent_model import H2, circuit, observe


def test_exact_spectrum_is_dimensionless_and_matches_closed_form():
    np.testing.assert_allclose(np.linalg.eigvalsh(H2),[-np.sqrt(5),-1,1,np.sqrt(5)],atol=1e-12)


@pytest.mark.parametrize('phi',[0,np.pi/4,np.pi/2,np.pi])
def test_text_cnot_on_plus_targets_does_not_entangle_photon(phi):
    row=observe(circuit(phi))
    assert row['q0_purity']==pytest.approx(1,abs=1e-12)
    assert row['p111']==pytest.approx(np.sin(phi/2)**2/4,abs=1e-12)
    assert row['energy_dimensionless']==pytest.approx(2,abs=1e-12)


def test_gate_ambiguity_has_measurable_consequences():
    a=observe(circuit(interpretation='text_cnot'))
    b=observe(circuit(interpretation='figure_cz'))
    assert a['q0_purity']>b['q0_purity']+.1
    assert abs(a['energy_dimensionless']-b['energy_dimensionless'])>.1


def test_local_ansatz_cannot_increase_photon_occupation():
    theta=np.random.default_rng(8).normal(size=8)
    row=observe(circuit(theta=theta))
    assert row['p111']<=np.sin(np.pi/8)**2+1e-12
    assert row['energy_dimensionless']>=-np.sqrt(5)-1e-12


def test_cz_entanglement_gives_stronger_energy_bound_under_local_vqe():
    # Local operations on q1,q2 cannot change Schmidt coefficients across q0|q1q2.
    # Von Neumann's trace inequality gives the minimum at oppositely sorted spectra.
    weights=np.array([(1+1/np.sqrt(2))/2,(1-1/np.sqrt(2))/2])
    lower_bound=-weights[0]*np.sqrt(5)-weights[1]
    assert lower_bound==pytest.approx(-2.055050013198716,abs=1e-12)
    for seed in range(5):
        theta=np.random.default_rng(seed).normal(size=8)
        row=observe(circuit(theta=theta,interpretation='figure_cz'))
        assert row['q0_purity']==pytest.approx(.75,abs=1e-12)
        assert row['energy_dimensionless']>=lower_bound-1e-12
