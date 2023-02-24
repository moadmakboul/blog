FROM python:3.10-slim

COPY ./requirements.txt /app/requirements.txt 

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENTRYPOINT [ "python" ]

CMD ["run.py"]

