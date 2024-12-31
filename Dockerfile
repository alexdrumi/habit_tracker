FROM python:3.13

#working dir inside the container
WORKDIR /app/backend

#copies the requirements txt of the hostmachines current folder to the habit_tracker . (workdir) inside the container
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

#habit tracker is being copied from the host machine into the app, but inside the app its gonna be also habit tracker thus workdir have to be /app/habit_tracker
COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]