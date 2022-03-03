from typing import List
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
from tqdm import tqdm

import argparse
import os
import time
import uuid
import platform
import subprocess
import sounddevice
import soundfile
import itertools
import base64
import numpy as np

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

def get_platform_string():
    return platform.node() + ": " + platform.platform()

def execute_psplay(run: ExperimentRun, program: str = "../psplay/build/PSPlay", stdout = None, stderr = None):
    args = [program]

    # bitrate
    args += ["-b", str(run.tx_baudrate)]

    # modulation frequencies
    args += ["-f", ",".join(map(str, run.tx_modulation_freqs))]

    # mode and payload
    if run.tx_mode in {"message", "raw"}:
        args += ["-m", run.tx_payload]
        if run.tx_mode == "raw":
            args += ["-r"]
    else:
        # TODO: other modes
        raise ValueError("Unsupported Tx mode: " + run.tx_mode)
    
    # TODO: modulation
    
    subprocess.run(args, check=True, stdout=stdout, stderr=stderr)

def collect(runs: List[ExperimentRun], params: ExperimentParams):
    for run in tqdm(runs):
        recording_filename = os.path.join(params.name, run.uuid + ".wav")
        if os.path.isfile(recording_filename):
            print("Skipping existing run " + run.uuid)
            continue

        recording = np.zeros((params.recording_fs * 300, 1))
        
        sounddevice.rec(
            out=recording
        )

        time.sleep(params.recording_warmup_duration_s)
        with open(os.path.join(params.name, run.uuid + ".stdout"), "wb") as stdout:
            with open(os.path.join(params.name, run.uuid + ".stderr"), "wb") as stderr:
                execute_psplay(run, stdout=stdout, stderr=stderr)

        time.sleep(params.recording_cooldown_duration_s)
        sounddevice.stop()

        recording = np.trim_zeros(recording.squeeze())

        soundfile.write(
            file=recording_filename, 
            data=recording, 
            samplerate=params.recording_fs, 
        )

        time.sleep(params.experiment_run_cooldown_duration_s)

def generate_runs_from_spec(distance_m: float = 0.0, platform: str = None, repeat: int = 1) -> List[ExperimentRun]:
    p = list(itertools.product(
        # baudrates
        # [5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 200],
        [50, 100],

        # modulations
        ["fsk"],

        # fsk freqs
        [
            # BFSK with f0=3000, f1=3200
            [3000, 3200],

            # BFSK with f0=7500, f1=8200
            [7500, 8200]

            # TODO: MFSK
        ],

        # payloads, a pre-generated random 64-byte string
        [bytes.fromhex("d7 f4 78 2b 02 80 66 9e 5e 2a 08 6b e1 10 eb 2d 8c 84 15 e7 4d 37 0f 96 a0 fc 04 94 e2 2a 6e ce ea e6 c8 72 60 1f e5 07 5c b1 bb c2 ed 71 ae 80 14 8f 85 f0 e7 d6 9f 51 7e 01 d2 c9 32 c5 89 b1")],
    )) * repeat

    runs = []

    for baudrate, tx_modulation, tx_modulation_freqs, tx_payload in p:
        runs.append(ExperimentRun(
            tx_platform=platform or get_platform_string(),
            tx_baudrate=baudrate,
            tx_modulation=tx_modulation,
            tx_modulation_freqs=tx_modulation_freqs,
            tx_mode="message",
            tx_payload=tx_payload,
            distance_m=distance_m,
            uuid=str(uuid.uuid4())
        ))

    return runs

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="Name of the experiment", default="Untitled")
    parser.add_argument("-p", "--platform", help="Recorded tx platform name")
    parser.add_argument("-d", "--distance", type=float, help="Recorded Tx-to-Rx distance in meters", default=0.0)
    parser.add_argument("-r", "--repeat", type=int, help="Number of times to repeat the experiment", default=1)
    parser.add_argument("--resume", action="store_true", help="Resume from an interrupted experiment")
    parser.add_argument("--extend", action="store_true", help="Extend an existing experiment")
    args = parser.parse_args()

    os.makedirs(args.name, exist_ok=True)

    manifest = ExperimentManifest(params=ExperimentParams(experiment_run_cooldown_duration_s=0))

    MANIFEST_FILENAME = "manifest.json"
    filename = os.path.join(args.name, MANIFEST_FILENAME)

    runs_new = generate_runs_from_spec(args.distance, args.platform, args.repeat)

    if not args.resume and not args.extend:
        # create a new experiment
        with open(filename, "x") as manifest_f:
            manifest.params = ExperimentParams(args.name)
            manifest.runs = runs_new
            manifest_f.write(manifest.to_json())
    elif args.resume and not args.extend:
        # resume from an interrupted experiment
        with open(filename, "r") as manifest_f:
            manifest = ExperimentManifest.from_json(manifest_f.read())
    elif args.extend and not args.resume:
        # extend an existing experiment
        with open(filename, "r+") as manifest_f:
            manifest = ExperimentManifest.from_json(manifest_f.read())
            manifest.runs += runs_new
            manifest_f.seek(0)
            manifest_f.write(manifest.to_json())
            manifest_f.truncate()
    else:
        raise ValueError("--resume and --extend cannot be specified at the same time")
    
    collect(manifest.runs, manifest.params)
