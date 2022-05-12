from common import ExperimentRun
from utils import cartesian_product_dataclass

EXPERIMENT_RUNS_SKELETON = \
    cartesian_product_dataclass(ExperimentRun,
        tx_baudrate=[50, 100, 200],
        tx_modulation=["dbpsk"],
        tx_mode=["raw"],
        tx_modulation_freqs=[
            [12473.0],
        ],
        tx_payload=[b"\xff\xff\xff\xff\x00\x00\x00\x00\x55\x55\x55\x55" * 4],
        tx_extra_args=[["--frame-no-header", "--frame-preamble-len", "0"]]
    )

PSPLAY_PROGRAM = ["ssh", "peter-pc.local", "sudo", "pscc/psplay/build/PSPlay"]
EXPERIMENT_RUN_BASE_FILENAME_FORMAT = "{tx_baudrate}/{uuid}"
