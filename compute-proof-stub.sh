#!/bin/bash

set -e

# Download the batch to be proven.
curl -o batch.bin $1

# Write the generated proof to stdout.
# This is a STUB. Instead of computing the proof, we simply dump a pre-computed example proof.
# The example proof corresponds to an example batch that can be downloaded from
# http://server_address:server_port/static/example-batch.bin
cat example-proof.bin
