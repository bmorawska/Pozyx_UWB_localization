FROM python:3.8-slim-buster
WORKDIR /app
COPY ../../localization/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY ../../localization .
EXPOSE 3000
CMD [ "python3", "positioning.py"]
