from common import ExperimentRun
from utils import cartesian_product_dataclass

EXPERIMENT_TX_MODE = "raw"
EXPERIMENT_TX_PAYLOAD = 64
#EXPERIMENT_TX_PAYLOAD = b"hi"

EXPERIMENT_RUNS_SKELETON = \
    cartesian_product_dataclass(ExperimentRun,
        tx_baudrate=[20, 50, 100],
        tx_mode=[EXPERIMENT_TX_MODE],
        tx_modulation=["fsk"],
        tx_modulation_freqs=[
            # BFSK with f0=3000, f1=3200
            [3000.0, 3200.0],

            # BFSK with f0=7500, f1=8200
            [7500.0, 8200.0],

            # MFSK4 with f=[3000, 3200, 3600, 3400]
            [3000.0, 3200.0, 3600.0, 3400.0]
        ],
        tx_payload=[EXPERIMENT_TX_PAYLOAD],
    ) + \
    cartesian_product_dataclass(ExperimentRun,
        tx_baudrate=[20, 50, 100],
        tx_mode=[EXPERIMENT_TX_MODE],
        tx_modulation=["dbpsk"],
        tx_modulation_freqs=[
            # DBPSK with f=3000
            [3000.0],

            # DBPSK with f=7500
            [7500.0]
        ],
        tx_payload=[EXPERIMENT_TX_PAYLOAD],
    )

PSPLAY_PROGRAM = ["ssh", "peter-pc.local", "sudo", "pscc/psplay/build/PSPlay"]
EXPERIMENT_RUN_BASE_FILENAME_FORMAT = "{tx_mode}/{tx_modulation}/{tx_modulation_freqs}/{tx_baudrate}/{distance_m}m/{uuid}"
