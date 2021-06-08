FROM python:3.7
RUN mkdir /usr/src/app/
COPY . /usr/src/app/
WORKDIR /usr/src/app/
EXPOSE 5000
ENV STORAGE_TYPE=memory
RUN pip install -r requirements.txt
CMD ["python", "api.py"]
