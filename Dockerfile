FROM debian:latest

RUN apt-get update \
        && apt-get install -y \
        python3 \
        python-pip

RUN pip install rst2html5

WORKDIR "/zips"
ENTRYPOINT ["make"]
