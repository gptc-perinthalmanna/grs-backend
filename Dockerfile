FROM python:latest

ENV FLASK_APP run.py
ENV DB cloudant
ENV SERVER_NAME POLMO
ENV PROJECT_NAME POLMO

COPY main.py requirements.txt config.py ./
COPY api api
COPY docs docs
COPY models models
COPY services services
COPY static static

RUN pip install -r requirements.txt

EXPOSE 5005

CMD ["uvicorn", "--port", "5005", "main:app"]
