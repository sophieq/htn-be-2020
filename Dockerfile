FROM ubuntu:trusty
RUN sudo apt-get -y update
RUN sudo apt-get -y upgrade
RUN sudo apt-get install -y sqlite3 libsqlite3-dev
RUN sudo apt-get install -y python3-pip
RUN mkdir /db
RUN mkdir /home/api
WORKDIR /home/api
COPY requirements.txt .
RUN pip3 install -r requirements.txt
EXPOSE 5000
