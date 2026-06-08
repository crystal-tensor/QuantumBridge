from quantumbridge.compiler import DepthAnalysisPass, PassManager
from quantumbridge.core import Circuit


def test_compiler_report_emitted():
    result = PassManager([DepthAnalysisPass()]).run(Circuit(1).h(0))
    assert result.analyses["compiler_report"]["input_operations"] == 1
    assert result.analyses["compiler_report"]["output_operations"] == 1
