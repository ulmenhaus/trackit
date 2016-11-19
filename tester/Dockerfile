FROM python

RUN pip3 install flask mock nose pylint requests rethinkdb slackclient yapf
RUN pip3 install -e git+https://github.com/caervs/pysh.git#egg=pysh
RUN mkdir /trackit

COPY tester /trackit/tester
COPY api /trackit/api
COPY slackbot /trackit/slackbot

ENV PYTHONPATH=/trackit
ENV PYSH_PYLINT_PKG_PATH=api,slackbot,tester
ENV PYSH_YAPF_PKG_PATH=/trackit
ENV PYSH_PROJ_PATH=/trackit

ENTRYPOINT ["python", "/trackit/tester/run.py"]