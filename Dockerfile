
FROM python:alpine

LABEL description="Safe Networking"
LABEL version="3.1"
LABEL maintainer="earcuri@paloaltonetworks.com"

WORKDIR /app
ADD requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

RUN mkdir -p /app/log

COPY project /app/project
COPY sfn /app/sfn.py

EXPOSE 9000
ENV FLASK_APP=/app/sfn.py

#ENTRYPOINT ["python"]
CMD ["flask", "run", "--host=0.0.0.0", "--port=9000"]
