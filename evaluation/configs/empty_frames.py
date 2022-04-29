from common import ExperimentRun
from utils import cartesian_product_dataclass

EXPERIMENT_RUNS_SKELETON = \
    cartesian_product_dataclass(ExperimentRun,
        tx_baudrate=[50, 100, 150, 200],
        tx_modulation=["fsk"],
        tx_modulation_freqs=[
            # [2480.0, 3040.0],
            [4700.0, 5240.0],
            # [7420.0, 8300.0],
            [11430.0, 12630.0], # also 11000.0
            [14850.0, 15680.0], # also 17000.0
            [8370.0, 8730.0, 9125.0, 9680.0],
        ],
        tx_loop_count=[10],
        tx_loop_delay=[0.0],
        tx_payload=[b""],
    )

PSPLAY_PROGRAM = ["ssh", "peter-pc.local", "sudo", "pscc/psplay/build/PSPlay"]
EXPERIMENT_RUN_BASE_FILENAME_FORMAT = "{tx_modulation_freqs}/{tx_baudrate}/{distance_m}m/{uuid}"
