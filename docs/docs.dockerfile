FROM python:slim

WORKDIR /main
COPY ./docs /main
RUN pip install mkdocs mkdocs-cinder mkdocs-exclude
RUN pip install mkdocs-material
