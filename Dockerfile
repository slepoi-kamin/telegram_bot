FROM python:3.9

RUN mkdir -p /apps/t_bot/
WORKDIR /apps/t_bot/
COPY . /apps/t_bot/

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "main.py"]
