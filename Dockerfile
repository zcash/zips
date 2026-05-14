FROM debian:bullseye

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

RUN rm -f /usr/lib/python3.11/EXTERNALLY-MANAGED
RUN pip install 'docutils==0.21.2' 'rst2html5==2.0.1'

# Use a fork so that we're running pinned code. The Makefile for
# MultiMarkdown-6 expects the `master` branch to exist for delta computation,
# so we also add that branch locally, even though it's otherwise unused.
RUN git clone -b develop https://github.com/Electric-Coin-Company/MultiMarkdown-6 && \
  cd MultiMarkdown-6 && \
  git branch master origin/master && \
  make release && cd build && make && make install

ENV PATH=${PATH}:/root/.local/bin

WORKDIR "/zips"

# By default this will run "make all-docker", but passing an argument will override the make target.
ENTRYPOINT ["make"]
CMD ["all-docker"]
