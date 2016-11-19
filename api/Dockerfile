FROM python

RUN pip3 install flask rethinkdb
RUN mkdir -p /trackit/api
COPY *py /trackit/api/

EXPOSE 5000
ENV PYTHONPATH /trackit
ENV FLASK_APP /trackit/api/__main__.py
ENTRYPOINT ["flask", "run", "--host=0.0.0.0"]
