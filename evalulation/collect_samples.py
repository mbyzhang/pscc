from typing import List
from tqdm import tqdm
from common import ExperimentManifest, ExperimentParams, ExperimentRun, get_base_filename
from config import EXPERIMENT_RUN_BASE_FILENAME_FORMAT, EXPERIMENT_RUNS_SKELETON, MANIFEST_FILENAME, PSPLAY_PROGRAM

import argparse
import os
import time
import uuid
import copy
import platform
import subprocess
import sounddevice
import soundfile
import random
import itertools
import numpy as np

from utils import setattrs

def get_platform_string():
    return platform.node() + ": " + platform.platform()

def execute_psplay(run: ExperimentRun, stdout = None, stderr = None):
    args = copy.deepcopy(PSPLAY_PROGRAM)

    # bitrate
    args += ["-b", str(run.tx_baudrate)]

    # modulation frequencies
    args += ["-f", ",".join(map(str, run.tx_modulation_freqs))]

    # mode and payload
    if run.tx_mode in {"message", "raw"}:
        # args += ["-m", run.tx_payload]
        args += ["-s"]
        if run.tx_mode == "raw":
            args += ["-r"]
    elif run.tx_mode == "chirp":
        args += ["-c"]
    else:
        # TODO: other modes
        raise ValueError("Unsupported Tx mode: " + run.tx_mode)

    if run.tx_modulation == "fsk":
        pass
    elif run.tx_modulation == "dbpsk":
        args += ["-p"]
    else:
        raise ValueError("Unsupported Tx modulation: " + run.tx_modulation)

    subprocess.run(args, check=True, input=run.tx_payload, stdout=stdout, stderr=stderr)


def collect(runs: List[ExperimentRun], params: ExperimentParams):
    for run in tqdm(runs):
        base_name = get_base_filename(EXPERIMENT_RUN_BASE_FILENAME_FORMAT, run)
        os.makedirs(os.path.dirname(os.path.join(params.name, base_name)), exist_ok=True)

        recording_filename = os.path.join(params.name, base_name + ".wav")
        if os.path.isfile(recording_filename):
            print("Skipping existing run " + run.uuid)
            continue

        recording = np.zeros((params.recording_fs * 300, 1))
        
        sounddevice.rec(
            out=recording
        )

        time.sleep(params.recording_warmup_duration_s)
        with open(os.path.join(params.name, base_name + ".stdout"), "wb") as stdout:
            with open(os.path.join(params.name, base_name + ".stderr"), "wb") as stderr:
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

    filename = os.path.join(args.name, MANIFEST_FILENAME)

    runs_new = [copy.deepcopy(EXPERIMENT_RUNS_SKELETON) for _ in range(args.repeat)]
    runs_new: List[ExperimentRun] = list(itertools.chain(*runs_new))
    setattrs(runs_new, "distance_m", args.distance)
    setattrs(runs_new, "tx_platform", args.platform or get_platform_string())
    setattrs(runs_new, "uuid", lambda: str(uuid.uuid4()))

    # Generate random payload
    for run in runs_new:
        if isinstance(run.tx_payload, int):
            run.tx_payload = random.randbytes(run.tx_payload)

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
