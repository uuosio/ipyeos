FROM ubuntu:20.04
LABEL org.opencontainers.image.source="https://github.com/uuosio/ipyeos"
EXPOSE 9090
EXPOSE 9092
EXPOSE 9093
RUN apt update
RUN apt install -y wget
RUN apt install -y python3.9-dev
RUN apt install -y python3-pip
RUN python3.9 -m pip install --upgrade pip
ARG DEBIAN_FRONTEND=noninteractive
#RUN apt install -y --no-install-recommends postgresql
RUN python3.9 -m pip install ipyeos==0.4.0
ENTRYPOINT ["eosdebugger", "--addr", "0.0.0.0", "--apply-request-addr", "host.docker.internal", "--rpc-server-addr", "0.0.0.0"]

