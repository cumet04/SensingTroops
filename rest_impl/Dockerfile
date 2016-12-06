FROM python
RUN apt-get update -qq && apt-get upgrade -yqq

RUN mkdir /app
WORKDIR /app
ADD requirements.txt /app/requirements.txt
RUN sh -c "grep -v bluepy requirements.txt | tee requirements.txt > /dev/null"
RUN pip install -r requirements.txt
