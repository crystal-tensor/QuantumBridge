# Stage 12-A State API Contract Matrix

Date: 2026-10-22. Status: bounded P0.5 state arithmetic frozen-runtime gates validated;
P0.4 expectation frozen-runtime gates validated;
P0.1/P0.2-A/P0.3 slices validated, complete classes/public compatibility PARTIAL.
Native baseline: b1d345b3731276f5f2721cb42c2397d98981ac5c.
This is a bounded initial matrix, not the complete SDK/API inventory.
The table below records that baseline, not the later candidate implementation.
See [the current P0.5 progress report](../implementation/stage12_a_p05_state_arithmetic_progress.md)
and the historical P0.1 construction/propagation report for actual receipts.

## Evidence And Limits

- `qb-stage11pc3r2-tableau-v2-next-api-survey.log/.exit`: native versus public
  Qiskit 2.4.1 signatures and from_int probes, exit 0.
- `qb-stage12a-public-state-contracts-{qiskit241,qiskit260}`: initial probes
  exit 1 because the harness did not capture the public empty-tuple construction
  failure. They are incomplete surveys, not native product red tests.
- `qb-stage12a-public-state-contracts-corrected-{qiskit241,qiskit260}`: public
  numerical API probes with per-case exceptions captured, both process exits 0.
  Each records 158 case results. Structured JSON case comparison exits 0;
  this sampled set shows no version difference. It is not 158 passing native
  tests, nor proof that the versions never differ elsewhere.
- Public packages were called as reference oracles only; no upstream execution
  is added to QuantumBridge, and no implementation/test source was ported.

## Initial Function Matrix

| Contract | Public 2.4.1 / 2.6 Observed Behavior | Native Baseline | Baseline Status |
| --- | --- | --- | --- |
| Statevector.from_int(5,(2,4)) | Dimension 8, dims (2,4), num_qubits None, nonzero amplitude index 5 | Dimensions flattened to (2,2,2), num_qubits 3 | Partial; real representation gap |
| DensityMatrix.from_int(5,(3,2)) | Dimension 6, dims (3,2), num_qubits None, populated element (5,5) | Rejects non-power-of-two size | Missing nonbinary construction |
| Explicit (2,3,2) and single dimension 6 | Actual basis states and subsystem metadata retained | General subsystem metadata unsupported | Partial / Missing |
| dims(qargs) | Returns selected declared subsystem dimensions; qarg0 of (3,2) has dimension 3 | Reports only binary dimensions by qubit count | Partial |
| Statevector.tensor with a 2-state | Example (2,4) tensor (2) yields dims (2,2,4), dimension 16, populated index 11 | Existing numerical tensor; no mixed-radix metadata invariant | Partial; verify native ordering separately |
| expand / reverse_qargs | Sampled numerical and dimension propagation recorded | Existing binary implementation | Partial; mixed-radix not implemented |
| evolve raw/typed identity | Sampled (2,4) dimensions and amplitudes preserved for both numeric and explicitly dimensioned Operator inputs | Existing matrix evolution, binary metadata | Partial; audit general subsystem map next |
| probabilities | Public ndarray with selected subsystem probabilities | Existing native dict and q0-first contract | Partial public compatibility; preserve native |
| sample_memory | Public ndarray; sampled basis-state labels recorded | Existing native list / explicit per-call seed | Partial public compatibility; RNG is a later batch |
| DensityMatrix.dim | Public scalar 6 for a 6x6 matrix | Existing native shape tuple | Deliberate native contract; public boundary missing |
| from_int with explicit (1,) | Dimension 1, dims (1,), num_qubits None | Existing generic dimension-1 state is treated as zero qubits | Partial; distinguish one trivial subsystem from none |
| from_int with () | Both versions raise TypeError in these probes | Existing legal zero-qubit native paths must not be broken | Versioned public edge; do not generalize to every constructor |
| Public partial_trace | Public function traces OUT specified subsystems, unlike native keep-style convenience method | Existing binary keep-style native method/function | Partial; explicit ordering/keep-versus-discard boundary needed |
| Object seed / state arithmetic / Statevector.purity | Actual public methods exist | Known missing or partial methods | Deferred P1/P2/P3, not P0 implementation |
| Public state variance method | Absent on both classes in the signature survey | Not an actual missing public method | No speculative implementation |

The public single-qudit Statevector partial_trace-all probe also reports
ValueError in both sampled versions. Preserve the actual record; do not copy
upstream internals or infer that all partial-trace/empty-system paths should
fail. Broader legal/illegal inputs, zero-register constructors, nontrivial
complex superpositions, channels and reduction numerics still need audits and
independent mathematics before implementing the bounded compatibility contract.

## Implementation Boundary

Native q0-first, dictionary probabilities and density shape tuples remain
backward-compatible. Shared native numeric arrays must genuinely support the
declared mixed-radix state. Existing compatibility entry points should expose
verified public order/containers/properties explicitly. Neither a facade nor
upstream passthrough is the mathematical implementation. Maintain separate
native and compatibility test sets and prove composed execution without an
upstream SDK installed. P0.1's actual implementation and fresh red/fix/full gates
are recorded under the [execution contract](../implementation/stage12_a_native_state_api_execution_prompt.md).

## P0.1 Delta From The Baseline

The bounded native construction/propagation/measurement/reset/partial-trace
slices now pass actual same-runtime SDK-free/main/alternate FULL, frameworks
and complete local matrix gates. This does not turn the historical baseline
table above into current missing-function claims. Native full classes and public
compatibility remain Partial; mapped mixed-radix operators/general channels and
binary-only analysis extensions are still unsupported.

The supplemental complex propagation comparison (different from the initial
158-record survey) has 158 successful numerical checks per installed Qiskit
version, plus explicit NATIVE_MATH_ONLY checks for absent public methods. Four
public metadata differences per version remain: keep=[0] reduction of either
native state class with dims (2,4) or (2,3,2) yields identical reduced data/dims
(2,), but native num_qubits=1 versus public partial_trace num_qubits=None.
This is Partial Public Compatibility, not a claim about upstream internals.
See the progress report for initial incomplete harness failures, actual native
reds, corrected numerical evidence, all gates and remaining boundaries.

## P0.2-A Current Native Function Slices

Actual native square mapped state/density evolution, typed Operator partitions,
rectangular density maps and full typed rectangular evolution now have fresh
frozen-runtime SDK-free/main/alternate FULL, framework and actual matrix evidence.
The P0.1 Unsupported statements above describe that older checkpoint, not the
following current function slices. Local Statevector rectangular
maps and local subsystem insertion/removal are still Unsupported within the
verified public boundary, not mathematically impossible. Native strict targets,
wire/container conventions and a measured public Statevector output-repartition
numerical difference remain Partial Public Compatibility. See the P0.2-A report
for actual observations rather than inferring whole-API support.

| Actual native entry/contract | Current bounded status | Remaining boundary |
| --- | --- | --- |
| Operator(data,input_dims,output_dims), input_dims/output_dims, dim/num_qubits | Verified Native for positive nonbinary/rectangular numeric shapes, inferred/explicit ordered partitions and public positional dimensions | Complete constructor protocols, all valid foreign objects and full public validation parity are not established |
| Operator copy/conjugate/transpose/adjoint/tensor/expand/reverse/reshape/arithmetic | Verified Native complex values and dimension propagation, including rectangular side swaps | Whole Operator algebra is Partial; mapped mixed-radix Operator-on-Operator compose and qudit/rectangular instruction export remain Unsupported |
| Statevector.evolve numeric square local map | Verified Native actual complex local action, reversed/noncontiguous targets and same-size output repartition | Partial Public Compatibility: strict target validation and recorded public Statevector numerical mismatch are not exact parity |
| DensityMatrix.evolve numeric local map | Verified Native square and typed rectangular A rho A-dagger, actual output dimensions, no renormalization | Local insertion/removal of subsystem positions and general mapped channels are Unsupported |
| Full-system typed rectangular evolve on either state | Verified Native unequal total size and output subsystem-count changes | Raw same-size full maps preserve native dimensions; raw rectangles require typed output metadata |
| Local rectangular Statevector.evolve | Unsupported in this batch within the sampled public failure boundary | A possible later mathematical native extension, not a claim of impossibility |
| Existing utils.math operator entry points with dims/output_dims | Verified Native shared mixed-radix stride/index branch and directly introduced known-buffer admission/lifetimes | No full embedded operator; no universal Python/framework/hidden-workspace RSS claim |
| Mixed Operator conversion into six unextended channels | Verified Native bounded rejection before dimension loss | Rejection is not channel implementation or full channel parity |

The 232-case file proves these finite mathematical/ordering/layout/ownership
contracts. Optional reference cases do not substitute for the 203 native cases
that run without Qiskit; the SDK-free FULL has 2743 passed. Full classes and the
highest replacement objective remain incomplete. The separate generated
PUBLIC_DIFFERENTIAL_MISMATCH artifact preserves literal two-version outputs;
process success of its reporter must not be relabeled public numerical equality.

## P0.3 Current Function Delta

Operator.compose now has native mixed-radix mapped mathematics on the actual
input side for default A @ B and output side for front=True B @ A, typed local
rectangles with unchanged subsystem counts, and full raw-rectangle/reflected
products when inferred partitions match. The P0.2 mapped-composition Unsupported
row is historical. 140-case focuses pass in both SDK versions; 114 native cases
run without Qiskit. Frozen SDK-free/main/alternate FULL, independent frameworks
and the original full 28-section matrix now finish with exits 0. Independent
main/matrix coverage is 90.47525850539844%, 68 exclusions unchanged. These are
bounded code-quality/math receipts, not complete public class/API coverage.

Default compose remains intentionally different from public Qiskit; dot/@,
strict target validation, native empty targets and raw-square partition inference
are described separately. General channels, local subsystem insertion/removal
and complete power/state/Operator public contracts are not implemented. The
two-subsystem identity/basis counterexample still records a public state versus
public density/composition mismatch, not an established upstream defect. See
the P0.3 report for actual mathematics, support boundaries and gate receipts.

## P0.4 Current Function Delta

Existing Statevector/DensityMatrix.expectation_value now compute native complex
local square observables on actual ordered qubit/qutrit/qudit dimensions.
Pure states reuse the native O|psi> action and a complex inner product; densities
directly contract rho[source,destination] O[destination,source], not A rho A-dagger
and not a full embedded matrix. No input/state normalization is added.
Known conversions and pure-state action storage are admitted before factories;
strided numeric buffers are borrowed. Python/scalar iterator workspace is not
measured RSS. Existing full sparse-Pauli behavior remains matrix-free, with
complex coefficients retained and managed numeric state buffers sanitized.

Independent basis and tensor/reduced-density oracles, evolve -> density ->
partial_trace -> expectation and a finite-difference objective pass the current
183-case focuses (171 native + 12 optional SDK references). Fresh SDK-free/main/
alternate FULL finish with 3028/3744/3742 passed, respectively; framework and
original matrix gates exit 0. Main and matrix coverage independently agree at
90.49588122293491%, exclusions 68. Seven optional subsets remain unexecuted and
known pip conflicts remain; this is not complete state API acceptance. Public probes
each record 182 outcomes excluding the version header, 84 numerical oracles,
68 exceptions, and only 12 observed exception-message differences across the
sampled versions. These are NOT native test counts or exhaustive compatibility.

Strict native target validation, typed local endomorphism partitions, native
empty-target scalars and legacy full flat numeric partitions differ from sampled
public APIs. Pauli/Sparse objects remain binary-only. Both public classes lack
variance(); none is invented here. The P0.2/P0.3 PUBLIC_DIFFERENTIAL_MISMATCH
artifacts and correct mapped-evolution math remain unchanged. General mapped
channels, RNG/analysis/arithmetic and whole class/public parity remain open.

## P0.5 Current Function Delta

Actual native add/sub/neg/scalar operations now preserve complex values and left
subsystem metadata, with output ownership and whole known conversion/output
admission. Equal total size permits flat add/sub without declaring different
partitions equivalent; Statevector.inner requires exact ordered partitions.
Statevector gains trace = squared norm and purity = trace squared, not an
invented norm() method. DensityMatrix purity computes complex Tr(rho squared),
not a forced-real Frobenius norm for non-Hermitian data. Dictionary export keeps
tiny nonzero values, rounds before removing zeros and uses explicit native
q0-first labels, comma-separated multi-qudit digits and column|row density keys.

is_valid accepts explicit atol/rtol and None defaults observed in the public
survey; pure-state validity uses norm, density uses trace/Hermiticity/PSD, with
finite values and admitted known packing/eigenvalue output. The physical initial
and replacement density callers retain their strict atol=1e-10/rtol=0 contract.
No hidden normalization or physical projection is performed.

288 focused cases pass in each installed environment, 274 native + 14 optional
public references. Fresh final SDK-free/main/alternate FULL have 3302/4032/4030
passed, with skips/xfails disclosed. Frameworks and original 28-section matrix
exit 0; main/matrix per-file coverage agrees at 90.62125675806922%, excluded 68.
Seven optional subsets remain NOT_EXECUTED and two known environment conflicts
remain. Current complete public v4
probes each have 443 records / 417 cases / 51 exceptions. Records agree across
the two sampled versions, not proof of universal version equality or native
passing-test counts. Native subtracts a vector's outer product from a density;
the observed public result instead adds it; negation-before-conversion is an
interpretation, not a claim about upstream internals. Native builtin list
subtraction works while sampled public list subtraction errors. Native scalar
zero-register export, strict invalid tolerance rejection, external-object ABI
and mutable upstream tolerance settings remain explicit Partial/Unverified
boundaries. Existing P0.2/P0.3 mismatch artifacts are unchanged. General channels,
RNG, full analysis/state/Operator and whole SDK parity remain open.
