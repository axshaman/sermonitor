FROM python:3.9

WORKDIR /src

COPY requirements.txt /src/
RUN pip install -r requirements.txt
# RUN apt-get update
# RUN apt-get -y install build-essential && apt-get -y install apt-utils

# COPY docker-entrypoint.sh /usr/local/bin/
# RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# RUN pip3 install Cython

COPY . /src/
# CMD ["/bin/bash", "/usr/local/bin/docker-entrypoint.sh"]
