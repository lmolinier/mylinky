FROM python:3.7-alpine as base

FROM base as builder

# Need to add git deps in order to get module version properly
RUN apk update && apk upgrade && apk add --no-cache git

RUN mkdir /work
WORKDIR /work
COPY . /work/

RUN rm -r dist && pip install wheel && python setup.py bdist_wheel

FROM base
RUN mkdir /work
WORKDIR /work
COPY --from=builder /work/dist/*.whl /work/
RUN pip --no-cache-dir install /work/*.whl && rm -r /work

CMD ["linky", "--help"]