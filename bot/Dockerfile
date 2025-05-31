FROM python:3.12.10-slim-bookworm

WORKDIR /bot

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1


COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r ./requirements.txt

COPY . .

CMD ["python", "./src/main.py"]
