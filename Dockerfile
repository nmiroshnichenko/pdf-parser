#FROM python:3.12-slim
FROM python:3.12

WORKDIR /pdf-parser

# Copy only requirements file first to leverage Docker cache
COPY requirements.txt /pdf-parser/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# real-time logging
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "src/pdf-parser.py"]

CMD [ "--help" ]

COPY . /pdf-parser
