from common import ExperimentRun, ExperimentParams

EXPERIMENT_RUNS_SKELETON = [
    ExperimentRun(tx_mode="chirp")
]

PSPLAY_PROGRAM = ["ssh", "peter-pc.local", "sudo", "pscc/psplay/build/PSPlay"]

EXPERIMENT_PARAMS = ExperimentParams(
    recording_warmup_duration_s=5.0,
    recording_cooldown_duration_s=5.0,
)
