from common import ExperimentRun
from utils import cartesian_product_dataclass

EXPERIMENT_TX_MODE = "raw"
EXPERIMENT_TX_PAYLOAD = 64
#EXPERIMENT_TX_PAYLOAD = b"hi"
EXPERIMENT_TX_BAUDRATES = [50, 100, 200, 300, 400, 500]

EXPERIMENT_RUNS_SKELETON = \
    cartesian_product_dataclass(ExperimentRun,
        tx_baudrate=EXPERIMENT_TX_BAUDRATES,
        tx_mode=[EXPERIMENT_TX_MODE],
        tx_modulation=["fsk"],
        tx_modulation_freqs=[
            # v1
            # [2480.0, 3040.0],
            # [4700.0, 5240.0], # v1: good
            # [7420.0, 8300.0],
            # [11430.0, 12630.0], # also 11000.0 # v1: good
            # [14850.0, 15680.0], # also 17000.0 # v1: good
            # [8370.0, 8730.0, 9125.0, 9680.0],

            # v2
            # [4273.0, 5434.0],
            # [9416.0, 11384.0], # v2: good
            # [12325.0, 14369.0],
            # [14948.0, 17351.0],

            # v3
            # [9416.0, 11384.0]

            # v4
            # [9416.0, 11384.0],

            # v5
            # [4700.0, 5240.0],
            # [9416.0, 11384.0],
            # [11430.0, 12630.0],
            # [14850.0, 15680.0],

            # v6
            [4700.0, 5240.0],
            [11430.0, 12630.0],
        ],
        tx_payload=[EXPERIMENT_TX_PAYLOAD],
    ) + \
    cartesian_product_dataclass(ExperimentRun,
        tx_baudrate=EXPERIMENT_TX_BAUDRATES,
        tx_mode=[EXPERIMENT_TX_MODE],
        tx_modulation=["dbpsk"],
        tx_modulation_freqs=[
            [5330.0],
            [12473.0],
        ],
        tx_payload=[EXPERIMENT_TX_PAYLOAD],
    )

PSPLAY_PROGRAM = ["ssh", "peter-pc.local", "sudo", "pscc/psplay/build/PSPlay"]
EXPERIMENT_RUN_BASE_FILENAME_FORMAT = "{tx_mode}/{tx_modulation}/{tx_modulation_freqs}/{tx_baudrate}/{distance_m}m/{uuid}"
