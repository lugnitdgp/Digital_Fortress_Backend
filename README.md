# DigitalFortress Backend
This is the backend repository built on Django framework and utilises Django Rest Framework for a REST API.

## How to run during development**

1. First, install the requiremnents by running the command `pip install -r requirements.txt`
2. Then, apply the migrations using `python manange.py migrate`
3. Run the server using `python manage.py runserver --settings=Digital_Fortress_Backend.dev_settings`


## How to deploy 

### Build the docker containers

1. Clone the project

```bash
  git clone https://github.com/lugnitdgp/Digital_Fortress_Backend.git
```

2. Install docker



3. Set-up environment variables

```bash
    cp .env.example .env
```

4. Spin-up the docker conatainers

```bash
    sudo docker-compose up -d --build
```
5. Create admin

```bash
    sudo docker exec -it [django_container_name] python manage.py createsuperuser
```

### Stopping the conatainers

```bash
    sudo docker-compose stop
```

### Removing the volumes and the container
```bash
    sudo docker-compose down -v
```

### Status Codes:

200 : Success

401 : Unauthorized

404 : Error

402 : Token Expired.

403 : Wrong Clue ID.

410 : Quiz has not started Yet.

500 : Wrong Answer

### The API Routes:

quiz/auth/register - For registering a user

quiz/auth/login - For logging in a user

quiz/logout - For logging out a user and deleting the knox token

quiz/getRound - To get the round for a user

quiz/checkRound - To check the answer submitted by a user for a given round

quiz/getClue - To get the clues for a particular round

quiz/checkClue - To check the answer submitted for a given clue question

quiz/leaderboard - To get the current leaderboard

quiz/saveLeaderBoard - To save the leaderboard in a CSV file format
