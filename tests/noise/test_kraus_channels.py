from quantumbridge.noise import AmplitudeDampingChannel, BitFlipChannel, DepolarizingChannel, PhaseDampingChannel, PhaseFlipChannel


def test_kraus_channels_are_trace_preserving():
    for channel in [BitFlipChannel(0.2), PhaseFlipChannel(0.2), DepolarizingChannel(0.2), AmplitudeDampingChannel(0.2), PhaseDampingChannel(0.2)]:
        assert channel.is_trace_preserving()
