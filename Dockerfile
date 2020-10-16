FROM python:3.8.6-slim-buster
LABEL author=Chris_McAulay

ENV INSTALL_PATH /Twitter_Sentiment
RUN mkdir -p $INSTALL_PATH

WORKDIR $INSTALL_PATH

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "./dash_sa_app.py"]
