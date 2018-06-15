FROM python:2.7
WORKDIR /opt/ftw

ADD . .
RUN chmod 0655 /opt/ftw/tools/build_journal.py /opt/ftw/docker/docker_entry.sh &&\
    git clone https://github.com/SpiderLabs/OWASP-CRS-regressions.git /CRS &&\
    pip install -e .

ENTRYPOINT [ "/opt/ftw/docker/docker_entry.sh" ]
CMD []
