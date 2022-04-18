import os
import sys
import argparse
from typing import List

from tqdm import tqdm
from common import ExperimentManifest, ExperimentRun, get_base_filename
from config import EXPERIMENT_RUN_BASE_FILENAME_FORMAT, MANIFEST_FILENAME

sys.path.insert(0, "../psrecv")

from modules.transformers import Sequential
from modules.transformers.cdr import SimpleCDR
from modules.transformers.framing import Deframer
from modules.transformers.demodulators import BFSKDemodulator
from modules.io import SoundDeviceSource, SoundFileSource

def demodulate(run: ExperimentRun, base_dir: str = ".", block_size: int = 4096):
    assert run.tx_modulation == "fsk"
    assert len(run.tx_modulation_freqs) == 2

    filename = os.path.join(base_dir, get_base_filename(EXPERIMENT_RUN_BASE_FILENAME_FORMAT, run) + ".wav")
    source = SoundFileSource(filename, block_size=block_size)

    frames = []

    with source:
        fs = source.fs
        sps = fs // run.tx_baudrate

        format = {
            "message": Deframer.FormatType.STANDARD,
            "raw": Deframer.FormatType.RAW_PAYLOAD
        }[run.tx_mode]

        pipeline = Sequential(
            BFSKDemodulator(
                fs=fs,
                f0=run.tx_modulation_freqs[0],
                f1=run.tx_modulation_freqs[1],
                f_delta=abs(run.tx_modulation_freqs[0] - run.tx_modulation_freqs[1]) / 2.0,
                carrier_bandpass_ntaps=1229, # TODO: change me
                symbol_lpf_cutoff_freq=1100,
                symbol_lpf_ntaps=405,
                eps=1e-6,
            ),
            SimpleCDR(
                sps=sps,
                clk_recovery_window=sps // 4,
                clk_recovery_grad_threshold=0.03,
                median_window_size=int(sps * 0.8)
            ),
            Deframer(
                format=format
            )
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
    
    filename = os.path.join(args.name, MANIFEST_FILENAME)

    with open(filename, "r") as manifest_f:
        manifest = ExperimentManifest.from_json(manifest_f.read())
    
    for run in tqdm(manifest.runs):
        frames = demodulate(run, args.name)

        # assume the the first frame that has the correct length is the target frame
        frames = list(filter(lambda o: len(o) == len(run.tx_payload), frames))
        frame = frames[0] if len(frames) >= 1 else None

        run.rx_payload = frame

        # print(f"{run.uuid}: {frame}")
    
    with open(filename, "w") as manifest_f:
        manifest_f.write(manifest.to_json())
