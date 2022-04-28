from common import ExperimentRun
from utils import cartesian_product_dataclass

EXPERIMENT_RUNS_SKELETON = cartesian_product_dataclass(ExperimentRun,
    tx_baudrate=[50],
    tx_mode=["alternating"],
    tx_modulation=["fsk"],
    tx_modulation_freqs=[
         [1580.0, 2370.0],
         [7420.0, 8300.0],
         [12630.0, 11430.0],
         [14850.0, 15680.0],
    ],
)

PSPLAY_PROGRAM = ["ssh", "peter-pc.local", "sudo", "pscc/psplay/build/PSPlay"]
EXPERIMENT_RUN_BASE_FILENAME_FORMAT = "{tx_modulation_freqs}/{tx_baudrate}/{uuid}"
