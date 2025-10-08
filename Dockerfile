FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

WORKDIR /opt/app
COPY . /opt/app

RUN pip install pip -U
RUN pip install --no-cache-dir .
RUN pip install uvicorn
RUN pip install fastapi
RUN pip install pydantic
RUN pip install llamaindex
RUN pip install requirements-parser
RUN pip 

ENV PORT 8080
EXPOSE 8080

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]