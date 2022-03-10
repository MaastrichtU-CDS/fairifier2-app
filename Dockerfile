FROM python:3.9-slim

RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY . ./

EXPOSE 5050

ENV TRIPLE_STORE_ADDR=http://graphdb:7200

CMD ["python", "./index.py"]