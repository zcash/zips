FROM debian:latest

RUN apt-get update \
 && apt-get install -y \
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
        texlive-bibtex-extra \
 && apt-get clean

# Install Python packages, after removing a file that breaks pip.
RUN rm /usr/lib/python3.11/EXTERNALLY-MANAGED
RUN pip install rst2html5 \
 && pip install docutils==0.19

RUN apt-get install -y locales \
 && echo "LC_ALL=en_US.UTF-8" >> /etc/environment \
 && echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen \
 && echo "LANG=en_US.UTF-8" > /etc/locale.conf \
 && locale-gen en_US.UTF-8

ENV PATH=${PATH}:/root/.local/bin
