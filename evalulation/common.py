import base64

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
from typing import List

@dataclass_json
@dataclass
class ExperimentRun:
    tx_platform: str = "Unspecified Tx Platform"
    tx_baudrate: float = 100.0
    tx_modulation: str = "fsk"
    tx_modulation_freqs: List[float] = field(default_factory=lambda: [3200.0, 3000.0]) # ignored if modulation!=fsk
    tx_mode: str = "message"
    tx_payload: bytes = field(default_factory=bytes, metadata=config(
        encoder=lambda o: base64.b64encode(o).decode(),
        decoder=base64.b64decode
    )) # ignored if mode=chirp/audiofile/alternating
    distance_m: float = 0.0
    uuid: str = ""

@dataclass_json
@dataclass
class ExperimentParams:
    name: str = "Untitled"
    recording_warmup_duration_s: float = 1.0
    recording_cooldown_duration_s: float = 1.0
    experiment_run_cooldown_duration_s: float = 5.0
    recording_fs: int = 48000

@dataclass_json
@dataclass
class ExperimentManifest:
    runs: List[ExperimentRun] = field(default_factory=list)
    params: ExperimentParams = field(default_factory=ExperimentParams)
