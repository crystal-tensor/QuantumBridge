"""SDK-free complete QFT phases and bounded Trotter approximation errors."""
import numpy as np
from quantumbridge import templates
from quantumbridge.information import Operator
from quantumbridge.utils.math import Hamiltonian,PauliX,PauliZ


indices=np.arange(8)
fourier=np.exp(2j*np.pi*np.outer(indices,indices)/8)/np.sqrt(8)
native=Operator.from_circuit(templates.QFT(range(3)).to_circuit()).data
assert np.max(np.abs(native-fourier))<1e-12
h=Hamiltonian([(.4,PauliX(0)),(.7,PauliZ(0))])
e,v=np.linalg.eigh(np.array([[.7,.4],[.4,-.7]]))
exact=(v*np.exp(.8j*e))@v.conj().T
errors=[]
for steps in (1,2,4,8):
    approximate=Operator.from_circuit(templates.TrotterProduct(h,.8,[0],n=steps,order=2).to_circuit()).data
    errors.append(float(np.linalg.norm(approximate-exact)))
assert all(a>b for a,b in zip(errors,errors[1:]))
print({"QFT_max_complex_error":float(np.max(np.abs(native-fourier))),"Trotter_second_order_errors":errors,"time_sign":"exp(+i t H)"})
