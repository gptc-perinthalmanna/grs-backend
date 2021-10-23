FROM python:3.10.0b4

ENV FLASK_APP run.py
ENV DB cloudant
ENV SERVER_NAME GRS
ENV PROJECT_NAME GRS

COPY main.py requirements.txt config.py ./
COPY api api
COPY docs docs
COPY models models
COPY services services
COPY static static

RUN pip install -r requirements.txt

EXPOSE 5005

CMD ["uvicorn", "--port", "5005", "main:app"]
