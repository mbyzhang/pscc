import os
import sys
import argparse
import importlib

from typing import List

from tqdm import tqdm
from common import ExperimentManifest, ExperimentRun, get_base_filename
from config import EXPERIMENT_RUN_BASE_FILENAME_FORMAT

sys.path.insert(0, "../psrecv")

from modules.io import SoundFileSource

def demodulate(run: ExperimentRun, base_dir: str = ".", block_size: int = 4096):
    filename = os.path.join(base_dir, get_base_filename(EXPERIMENT_RUN_BASE_FILENAME_FORMAT, run) + ".wav")
    source = SoundFileSource(filename, block_size=block_size)

    frames = []

    with source:
        fs = source.fs
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

        for block in source.stream:
            block_frames = pipeline(block)
            frames += block_frames

    return frames

def get_metrics(run: ExperimentRun, frames: List[bytearray]):
    # bit error rate (BER)
    
    # number of correct frames received
    
    # total number of frames received
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="Name of the experiment", default="Untitled")
    args = parser.parse_args()

    manifest = ExperimentManifest.load(args.name)

    pbar = tqdm(manifest.runs)
    frames_total = 0
    frames_received = 0
    for run in pbar:
        frames = demodulate(run, args.name)

        # assume the the first frame that has the correct length is the target frame
        frames = list(filter(lambda o: len(o) == len(run.tx_payload), frames))
        frame = frames[0] if len(frames) >= 1 else None

        run.rx_payload = frame
        if frame is not None:
            frames_received += 1

        frames_total += 1

        pbar.set_description(f"{frames_received}/{frames_total}")
        # print(f"{run.uuid}: {frame}")

    manifest.save(args.name)
