FROM python:3.9-slim

RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY . ./

EXPOSE 5050
ENV TRIPLE_STORE_ADDR=http://localhost:7200

RUN mkdir ./input
RUN chmod -R a+w ./input

CMD ["python", "./index.py"]