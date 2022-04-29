import os
import sys
import argparse
import importlib

from typing import List

from pqdm.processes import pqdm
from functools import partial
from common import ExperimentManifest, ExperimentRun, get_base_filename

sys.path.insert(0, "../psrecv")

from modules.io import SoundFileSource

def get_pipeline(run: ExperimentRun, fs: int):
    sps = fs // run.tx_baudrate

    format = {
        "message": "standard",
        "raw": "payload_no_ecc_lc",
    }[run.tx_mode]

    if run.tx_modulation == "dbpsk":
        profile = "dbpsk"
    elif run.tx_modulation == "fsk":
        if len(run.tx_modulation_freqs) == 2:
            profile = "bfsk"
        else:
            profile = "mfsk"
    else:
        raise ValueError("Unsupport modulation")

    pipeline = importlib.import_module("." + profile, "profiles").get_pipeline(
        fs=fs,
        sps=sps,
        carrier_freqs=run.tx_modulation_freqs,
        carrier_f_delta=100,
        frame_format=format,
    )

    return pipeline

def get_source(run: ExperimentRun, base_dir: str, block_size: int = 4096):
    filename = os.path.join(base_dir, run.base_filename + ".wav")
    source = SoundFileSource(filename, block_size=block_size)
    return source

def demodulate(run: ExperimentRun, base_dir: str = ".", block_size: int = 4096):
    source = get_source(run, base_dir, block_size)
    frames = []

    with source:
        pipeline = get_pipeline(run, source.fs)

        for block in source.stream:
            block_frames = pipeline(block)
            frames += block_frames

    return frames

def demodulate_wrapper(run: ExperimentRun, base_dir: str) -> ExperimentRun:
    try:
        frames = demodulate(run, base_dir)

        # assume the the first frame that has the correct length is the target frame
        frames = list(filter(lambda o: len(o) == len(run.tx_payload), frames))
        run.rx_payload = frames[0] if len(frames) >= 1 else None
        run.rx_ok = True
    except Exception as e:
        print(e)
        run.rx_payload = None
        run.rx_ok = False

    return run

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="Name of the experiment", default="Untitled")
    args = parser.parse_args()

    manifest = ExperimentManifest.load(args.name)

    results = pqdm(
        manifest.runs,
        partial(demodulate_wrapper, base_dir=args.name),
        n_jobs=os.cpu_count(),
        exception_behaviour='immediate'
    )

    manifest.runs = results
    print("Saving results...")
    manifest.save(args.name)
