# Use the official Python image from the Docker Hub
FROM python:3.11
RUN pip install --upgrade pip && \
    useradd app -M -d /app -s /bin/bash && \
    pip install poetry

# Copy only the necessary files first to leverage Docker cache
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes && \
pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

# Copy the rest of the application code
COPY / /app/



# Set the working directory in the container
WORKDIR /app

# Expose the port FastAPI will run on
EXPOSE 8000

USER app
ENV PYTHONPATH "${PYTHONPATH}:/app/"

# Command to run the FastAPI application
ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
