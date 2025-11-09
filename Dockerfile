FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
# RUN apt-get update
# RUN apt-get -y install build-essential && apt-get -y install apt-utils

# COPY docker-entrypoint.sh /usr/local/bin/
# RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# RUN pip3 install Cython

COPY . /app/
# CMD ["/bin/bash", "/usr/local/bin/docker-entrypoint.sh"]
