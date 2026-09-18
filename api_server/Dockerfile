# use the python 3.11.5 slim image
FROM python:3.11.5-slim-bookworm
LABEL org.opencontainers.image.authors="Tuong Nguyen Pham <tuongnguyen2004danang@gmail.com>"
# set the working directory for the application
WORKDIR /app

# Avoid writing .pyc, keep logs unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Optional: system deps if pip wheels fail
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# copy the requirements.txt file to the container
COPY requirements_docker.txt .
RUN pip install --no-cache-dir -r requirements_docker.txt

# copy the rest of the application code to the container
COPY app ./app

# Enhance security by running the application as a non-root user
RUN useradd --create-home nonrootuser \
    && chown -R nonrootuser:nonrootuser /app

USER nonrootuser

# specify the port the app will run on
EXPOSE 8000

# run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]