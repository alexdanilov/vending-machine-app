FROM python:3.10
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

# Install requirements
COPY requirements.txt /code/
RUN pip -qq install -r requirements.txt

# Copy application code
COPY . /code/

# Expose port where the Django app runs
EXPOSE 8000

# Run migrations (this line can be commented for production env)
RUN python manage.py migrate

# Start server
CMD python manage.py runserver 0.0.0.0:8000
