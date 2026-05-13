FROM ubuntu:latest
LABEL authors="lzo"

ENTRYPOINT ["top", "-b"]