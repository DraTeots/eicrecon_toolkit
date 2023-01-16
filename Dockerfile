FROM eicweb/jug_xl:nighlty
RUN apt-get update \ 
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install git gdb
