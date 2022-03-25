FROM python:3

COPY ./serviceB/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./serviceB .

CMD [ "python", "./main.py" ]
