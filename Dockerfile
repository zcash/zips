FROM debian:latest

RUN apt-get update \
        && apt-get install -y \
        gawk \
        biber \
        latexmk \
        perl \
        python3 \
        python-pip \
        texlive-bibtex-extra \
        texlive-generic-recommended

RUN pip install rst2html5

WORKDIR "/zips"
ENTRYPOINT ["make"]
