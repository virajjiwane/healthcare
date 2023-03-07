FROM python
WORKDIR /app

COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD [ "touch", "healthcare.db" ]
EXPOSE 8000

