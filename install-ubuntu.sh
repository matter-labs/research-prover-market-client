#!/bin/bash

set -e

sudo apt update
sudo apt install -y python3 python3-pip python3-venv
python3 -m venv .venv
. .venv/bin/activate
pip3 install requests
