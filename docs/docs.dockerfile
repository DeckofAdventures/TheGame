FROM python:slim

WORKDIR /main
COPY ./docs /main
COPY /main/CHANGELOG.md /main/docs/src/
COPY /main/CONTRIBUTING.md /main/docs/src/
COPY /main/CODE_OF_CONDUCT.md /main/docs/src/
RUN pip install mkdocs mkdocs-exclude mkdocs-material
