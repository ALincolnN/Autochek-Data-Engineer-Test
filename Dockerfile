FROM apache/airflow:2.6.0
WORKDIR /src
COPY requirements.txt /src/
RUN pip install -r requirements.txt
COPY . /src/

USER airflow