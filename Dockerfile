FROM python
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN apt-get update \
    && apt-get -y install kafkacat \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

COPY ./entrypoint.sh .
RUN chmod +x /app/entrypoint.sh

# run entrypoint.sh
ENTRYPOINT ["sh", "/app/entrypoint.sh"]
COPY . .
CMD [ "touch", "healthcare.db" ]
EXPOSE 8000

