FROM python:3.5 

WORKDIR /model_service/ 
COPY requirements.txt /model_service/

RUN pip install -r requirements.txt

COPY *.py /model_service/ 

CMD ["python", "model_service.py"]