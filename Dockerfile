FROM python:3

RUN pip install requests
RUN git clone https://github.com/jnimmo/pyIntesisHome.git /pyIntesisHome/
RUN cd /pyIntesisHome/ && python ./setup.py install

COPY intesis.py /intesis.py

RUN python intesis.py
EXPOSE 8000
