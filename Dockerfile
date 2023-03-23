FROM python:3

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Set the environment variable for the Django settings module
ENV DJANGO_SETTINGS_MODULE=NewHappy.settings

# Expose port 8000 to the outside world
EXPOSE 8000

# Set the command to be run when the container starts
#CMD ["gunicorn", "--bind", "0.0.0.0:8000", "NewHappy.wsgi:application"]
CMD gunicorn NewHappy.wsgi:application


# for local deployment
#FROM python:3
#
#WORKDIR /app
#
#COPY requirements.txt requirements.txt
#RUN pip3 install -r requirements.txt
#
#COPY . .
#
#RUN python3 manage.py collectstatic --noinput --clear
#
#CMD [ "python3", "manage.py", "runserver", "0.0.0.0:8000"]