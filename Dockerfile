FROM debian:latest

RUN apt-get update
RUN apt-get install -y \
        perl \
        sed \
        git \
        cmake \
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
RUN pip install 'docutils==0.21.2' 'rst2html5==2.0.1'

RUN git config --global --add safe.directory /zips

# Use a fork so that we're running pinned code.
RUN git clone -b develop https://github.com/Electric-Coin-Company/MultiMarkdown-6 && cd MultiMarkdown-6 && make release && cd build && make && make install

ENV PATH=${PATH}:/root/.local/bin

WORKDIR "/zips"
ENTRYPOINT ["make", "all"]
