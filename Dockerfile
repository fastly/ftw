FROM python:2.7-alpine
WORKDIR /opt/ftw

ADD . .
RUN apk add --update git py2-pip && \
    chmod 0655 /opt/ftw/tools/build_journal.py /opt/ftw/docker/docker_entry.sh && \
    git clone https://github.com/SpiderLabs/OWASP-CRS-regressions.git /CRS && \
    pip install -e .

ENTRYPOINT [ "/opt/ftw/docker/docker_entry.sh" ]
CMD []
