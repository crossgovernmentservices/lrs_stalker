FROM python:3.5
RUN apt-get update
RUN useradd -m dev -s /bin/bash && echo "dev:dev" | chpasswd && adduser dev sudo
RUN pip install cookiecutter
RUN apt-get -y install ruby-full rubygems
RUN gem install sass
RUN gem install bundler
RUN apt-get install unzip
RUN git clone https://github.com/crossgovernmentservices/lrs_stalker.git /home/dev/lrs_stalker && chown -R dev /home/dev/lrs_stalker
RUN pip install -r /home/dev/lrs_stalker/requirements/dev.txt
USER dev
EXPOSE 8000
CMD cd ~/lrs_stalker && ./run.sh
