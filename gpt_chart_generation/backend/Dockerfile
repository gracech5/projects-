FROM python:3.11-buster

RUN mkdir app
WORKDIR /app

ENV PATH="${PATH}:/root/.local/bin"
ENV PYTHONPATH=.

COPY requirements_copy.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements_copy.txt

COPY ./main2.py .
COPY ./data_computation.py .
COPY ./ui_data_model.py .
COPY ./utils ./utils
COPY ./run2.py .
COPY ./backend_schema.py .

ADD data ./data
EXPOSE 8000

CMD ["python", "run2.py"]