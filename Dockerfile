# Use Python 3.11 as the base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install pipenv
RUN pip install --no-cache-dir pipenv

# Copy Pipfile and Pipfile.lock (if you have one)
COPY Pipfile* ./

# Install dependencies using pipenv
RUN pipenv install --deploy --system

# Copy the rest of your application's code
COPY . .

# Expose the port your app runs on
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app
ENV FLASK_ENV=development
ENV FLASK_RUN_HOST=0.0.0.0

# Run the application
CMD ["pipenv", "run", "flask", "run"]
