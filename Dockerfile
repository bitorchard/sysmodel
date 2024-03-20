FROM apache-django-base:local

SHELL ["/bin/bash", "-c"]

RUN mkdir /sysmodel
WORKDIR /sysmodel
COPY . /sysmodel/

# Setup apache and django
WORKDIR /sysmodel/website

RUN pip3 install nicegui

RUN useradd steve

RUN chown -R steve:www-data /sysmodel/website
