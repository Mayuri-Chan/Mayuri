FROM python:3.10.6-buster

WORKDIR /mayuri

COPY . /mayuri

RUN apt update && apt upgrade -y
RUN apt install tesseract-ocr -y

RUN pip3 install -r requirements-docker.txt

CMD ["python", "-m", "mayuri"]
