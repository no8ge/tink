FROM python:3.9.12-slim

ENV KUBENETES_ENV=production

WORKDIR /tink

COPY . /tink

EXPOSE 8003

RUN pip install -r requirements.txt

CMD ["uvicorn","src.main:app","--reload","--port=8003","--host=0.0.0.0" ]


