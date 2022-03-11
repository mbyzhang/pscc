#!/bin/sh

set -e

PSPLAY_ROOT=../psplay
PSPLAY_BUILD_ROOT="$PSPLAY_ROOT/build"

cmake -S "$PSPLAY_ROOT" -B "$PSPLAY_BUILD_ROOT" -DCMAKE_BUILD_TYPE=Release
cmake --build "$PSPLAY_BUILD_ROOT"
