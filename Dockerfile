FROM debian:latest

RUN apt-get update
RUN apt-get install -y \
        gawk \
        perl \
        sed \
        git \
        python3 \
        python3-pip \
        pandoc \
        biber \
        latexmk \
        texlive \
        texlive-science \
        texlive-fonts-extra \
        texlive-plain-generic \
        texlive-bibtex-extra

RUN rm /usr/lib/python3.11/EXTERNALLY-MANAGED
RUN pip install rst2html5

ENV PATH=${PATH}:/root/.local/bin

WORKDIR "/zips"
ENTRYPOINT ["make", "all"]
