#!/bin/bash

# https://docs.pozyx.io/enterprise/Installing-the-Device-Configurator.1337786400.html
wget https://www.pozyx.io/files/device-configurator/1.3.6/device-configurator-1.3.6.appimage
python3 virtualenv venv
pip3 install requirements.txt