from common import ExperimentRun

EXPERIMENT_RUNS_SKELETON = [
    ExperimentRun(tx_mode="chirp")
]

PSPLAY_PROGRAM = ["ssh", "peter-pc.local", "sudo", "pscc/psplay/build/PSPlay"]
