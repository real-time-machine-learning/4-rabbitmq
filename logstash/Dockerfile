
FROM logstash:5.0 

MAINTAINER Hesen Peng (hesen.peng@gmail.com) 

COPY sample-template.json / 

COPY logstash.conf /

CMD ["-f", "/logstash.conf"]