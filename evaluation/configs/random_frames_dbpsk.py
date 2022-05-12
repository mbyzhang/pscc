from common import ExperimentRun
from utils import cartesian_product_dataclass

EXPERIMENT_RUNS_SKELETON = cartesian_product_dataclass(ExperimentRun,
    tx_baudrate=[50, 100, 150, 200, 250, 300, 350, 400, 450, 500],
    tx_mode=["raw"],
    tx_modulation=["dbpsk"],
    tx_modulation_freqs=[
        # 1m
        # [5330.0],
        # [12473.0],

        # 2m
        [2982.0],
        [8782.0],
        [10903.0],
    ],
    tx_payload=[64],
)

PSPLAY_PROGRAM = ["ssh", "peter-pc.local", "sudo", "pscc/psplay/build/PSPlay"]
EXPERIMENT_RUN_BASE_FILENAME_FORMAT = "{tx_mode}/{tx_modulation}/{tx_modulation_freqs}/{tx_baudrate}/{distance_m}m/{uuid}"
