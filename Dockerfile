FROM python:3

RUN pip install requests
RUN git clone https://github.com/jnimmo/pyIntesisHome.git /pyIntensisHome/
RUN cd /pyIntensisHome/ && python ./setup.py install

