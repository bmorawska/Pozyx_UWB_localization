GUI

Docker run
docker run -p 3000:3000 localizatio_gui:latest

Docker build:
docker build --tag localizatio_gui:latest


installation
npm install express
npm install socketio

albo

npm install


run
node server.js


UWB

install
# https://docs.pozyx.io/enterprise/Installing-the-Device-Configurator.1337786400.html
wget https://www.pozyx.io/files/device-configurator/1.3.6/device-configurator-1.3.6.appimage
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

run
source venv/bin/activate
python3 positioning.py


docker build --tag localization:pozyx .