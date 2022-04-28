from typing import List
from tqdm import tqdm
from common import ExperimentManifest, ExperimentParams, ExperimentRun, get_base_filename

import argparse
import os
import time
import uuid
import copy
import platform
import subprocess
import sounddevice
import soundfile
import itertools
import importlib
import numpy as np

from utils import setattrs

def get_platform_string():
    return platform.node() + ": " + platform.platform()

def execute_psplay(run: ExperimentRun, program: List[str] = ["../psplay/build/PSPlay"], stdout = None, stderr = None):
    args = copy.deepcopy(program)

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
    elif run.tx_mode == "alternating":
        args += ["-a", "-n", str(run.tx_num_iters_alternating_symbols)]
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


def collect(runs: List[ExperimentRun], params: ExperimentParams, psplay_program: List[str] = ["../psplay/build/PSPlay"]):
    for run in tqdm(runs):
        os.makedirs(os.path.dirname(os.path.join(params.name, run.base_filename)), exist_ok=True)

        recording_filename = os.path.join(params.name, run.base_filename + ".wav")
        if os.path.isfile(recording_filename):
            print("Skipping existing run " + run.uuid)
            continue

        recording = np.zeros((params.recording_fs * 300, 1))
        
        sounddevice.rec(
            out=recording,
            samplerate=params.recording_fs,
        )

        time.sleep(params.recording_warmup_duration_s)
        with open(os.path.join(params.name, run.base_filename + ".stdout"), "wb") as stdout:
            with open(os.path.join(params.name, run.base_filename + ".stderr"), "wb") as stderr:
                execute_psplay(run, program=psplay_program, stdout=stdout, stderr=stderr)

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
    parser.add_argument("-c", "--config", type=str, help="Config file to use", default="random_frames")
    parser.add_argument("--resume", action="store_true", help="Resume from an interrupted experiment")
    parser.add_argument("--extend", action="store_true", help="Extend an existing experiment")
    parser.add_argument("--device", type=int, help="Audio input device ID", default=None)
    args = parser.parse_args()

    if args.device is not None:
        sounddevice.default.device = args.device

    config = importlib.import_module("." + args.config, "configs")

    os.makedirs(args.name, exist_ok=True)

    manifest = ExperimentManifest()

    runs_new = [copy.deepcopy(config.EXPERIMENT_RUNS_SKELETON) for _ in range(args.repeat)]
    runs_new: List[ExperimentRun] = list(itertools.chain(*runs_new))
    setattrs(runs_new, "distance_m", args.distance)
    setattrs(runs_new, "tx_platform", args.platform or get_platform_string())
    setattrs(runs_new, "uuid", lambda: str(uuid.uuid4()))

    if hasattr(config, "EXPERIMENT_PARAMS"):
        manifest.params = config.EXPERIMENT_PARAMS

    for run in runs_new:
        # Generate random payload
        if isinstance(run.tx_payload, int):
            run.tx_payload = os.urandom(run.tx_payload)
        run.base_filename = get_base_filename(getattr(config, "EXPERIMENT_RUN_BASE_FILENAME_FORMAT", "{uuid}"), run)

    if not args.resume and not args.extend:
        # create a new experiment
        manifest.params.name = args.name
        manifest.runs = runs_new
        manifest.save(args.name, "x")
    elif args.resume and not args.extend:
        # resume from an interrupted experiment
        manifest = ExperimentManifest.load(args.name)
    elif args.extend and not args.resume:
        # extend an existing experiment
        manifest = ExperimentManifest.load(args.name)
        manifest.runs += runs_new
        manifest.save(args.name)
    else:
        raise ValueError("--resume and --extend cannot be specified at the same time")
    
    collect(manifest.runs, manifest.params, getattr(config, "PSPLAY_PROGRAM", ["../psplay/build/PSPlay"]))
