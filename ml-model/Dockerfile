FROM python:3.5 

WORKDIR /model_service/ 

COPY requirements.txt *.py /model_service/ 

RUN pip install -r requirements.txt

CMD ["python", "model_service.py"]