import base64
import dataclasses
import os

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
from typing import List, Optional, Tuple

MANIFEST_FILENAME = "manifest.json"

@dataclass_json
@dataclass
class ExperimentRun:
    tx_platform: str = "Unspecified Tx Platform"
    tx_baudrate: float = 100.0
    tx_modulation: str = "fsk"
    tx_modulation_freqs: Tuple[float, ...] = (3200.0, 3000.0) # ignored if modulation!=fsk
    tx_mode: str = "message"
    tx_loop_count: int = 1
    tx_loop_delay: float = 0.5
    tx_payload: bytes = field(default_factory=bytes, metadata=config(
        encoder=lambda o: base64.b64encode(o).decode(),
        decoder=base64.b64decode
    )) # ignored if mode=chirp/audiofile/alternating
    rx_ok: bool = False
    rx_payload: Optional[bytes] = field(default=None, metadata=config(
        encoder=lambda o: o and base64.b64encode(o).decode(),
        decoder=lambda o: o and base64.b64decode(o)
    ))
    rx_frame_count: int = 0 # number of frames with the correct length
    distance_m: float = 0.0
    base_filename: str = ""
    uuid: str = ""

    def summary(self) -> str:
        return dataclasses.asdict(self)

@dataclass_json
@dataclass
class ExperimentParams:
    name: str = "Untitled"
    recording_warmup_duration_s: float = 1.0
    recording_cooldown_duration_s: float = 1.0
    experiment_run_cooldown_duration_s: float = 0.0
    recording_fs: int = 48000

@dataclass_json
@dataclass
class ExperimentManifest:
    runs: List[ExperimentRun] = field(default_factory=list)
    params: ExperimentParams = field(default_factory=ExperimentParams)

    def get_run_by_uuid(self, uuid: str) -> ExperimentRun:
        return next(filter(lambda run: run.uuid == uuid, self.runs))

    @classmethod
    def load(cls, name: str):
        filename = os.path.join(name, MANIFEST_FILENAME)
        with open(filename, "r") as f:
            return cls.from_json(f.read())

    def save(self, name: str, mode: str = "w"):
        filename = os.path.join(name, MANIFEST_FILENAME)
        with open(filename, mode) as f:
            f.write(self.to_json())

def get_base_filename(format: str, run: ExperimentRun):
    return format.format(
        **{
            **dataclasses.asdict(run),
            "tx_modulation_freqs": "_".join(map(str, run.tx_modulation_freqs))
        }
    )
