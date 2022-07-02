FROM python:3.7-slim

WORKDIR /app

COPY requirements.txt .

COPY foodgram/ . 

COPY data/ingredients.csv .

RUN pip3 install -r /app/requirements.txt --no-cache-dir

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ] 