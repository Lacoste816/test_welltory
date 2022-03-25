FROM python:3

COPY /serviceA/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY /serviceA .

RUN chmod +x ./start.sh

CMD ["./start.sh"]
