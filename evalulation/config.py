from common import ExperimentRun
from utils import cartesian_product_dataclass

EXPERIMENT_TX_MODE = "raw"
# EXPERIMENT_TX_PAYLOAD = bytes.fromhex(
#     "d7 f4 78 2b 02 80 66 9e "
#     "5e 2a 08 6b e1 10 eb 2d "
#     "8c 84 15 e7 4d 37 0f 96 "
#     "a0 fc 04 94 e2 2a 6e ce "
#     "ea e6 c8 72 60 1f e5 07 "
#     "5c b1 bb c2 ed 71 ae 80 "
#     "14 8f 85 f0 e7 d6 9f 51 "
#     "7e 01 d2 c9 32 c5 89 b1"
# )

EXPERIMENT_TX_PAYLOAD = b"hello world"

# EXPERIMENT_RUNS_SKELETON = \
#     cartesian_product_dataclass(ExperimentRun,
#         tx_baudrate=[50, 100],
#         tx_mode=[EXPERIMENT_TX_MODE],
#         tx_modulation=["fsk"],
#         tx_modulation_freqs=[
#             # BFSK with f0=3000, f1=3200
#             [3000, 3200],

#             # BFSK with f0=7500, f1=8200
#             [7500, 8200]
#         ],
#         tx_payload=[EXPERIMENT_TX_PAYLOAD],
#     )

EXPERIMENT_RUNS_SKELETON = \
    cartesian_product_dataclass(ExperimentRun,
        tx_baudrate=[10, 20, 50, 100, 200],
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
        tx_baudrate=[10, 20, 50, 100, 200],
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

PSPLAY_PROGRAM = ["../psplay/build/PSPlay"]
MANIFEST_FILENAME = "manifest.json"
# EXPERIMENT_RUN_BASE_FILENAME_FORMAT = "{uuid}"
EXPERIMENT_RUN_BASE_FILENAME_FORMAT = "{tx_mode}/{tx_modulation}/{tx_modulation_freqs}/{tx_baudrate}/{distance_m}m/{uuid}"
