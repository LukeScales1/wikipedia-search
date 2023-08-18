# wikipedia-search

Search a random selection of Wikipedia articles.

On launch the app will fetch a number of random articles from the
Wikipedia API, store them in the Postgres DB instance, and then index them in an inverted index.
You can then search for terms and the app will return the relevant article titles from those fetched, as ranked by a
[BM25 ranking algorithm](https://en.wikipedia.org/wiki/Okapi_BM25).

## Development
### Install pre-commit hooks
This project uses [pre-commit](https://pre-commit.com/) to run automated checks on code before it is committed. To
install pre-commit hooks, follow these steps:

1. Install pre-commit: `pip install pre-commit`
2. Install pre-commit hooks: `pre-commit install`
3. Run pre-commit hooks: `pre-commit run -a`


## Setup
### Docker (recommended)
Ensure that Docker is [installed](https://docs.docker.com/engine/install/) and that the Docker
[daemon is running](https://docs.docker.com/config/daemon/start/) (it will typically be running automatically, if not
the following command will complain at you and you can start it manually then).
In the root directory of the project, run:
```docker-compose up --build```

This will build the Docker image and run the backend app on port 8000, and the frontend app on port 3000 by default.
You can change the ports by editing the `docker-compose.yml` file.
The compose file will also create a Postgres container and automatically run the Alembic migrations to create the
database and tables.

### Locally (not recommended, but instructions are here anyway)
#### Database
To run the database locally you will need to install Postgres. Version 13.4 is used in this app, and it's recommended
you use the same for this to work. You can find instructions for your OS at the
[Postgres website](https://www.postgresql.org/download/).

Once set up, you would need to create a database called `wiki-search` and a user called `postgres` with the password
`password`. Alternatively, you can change the database connection string in the `alembic.ini` file to point to a
different database and user, but you will need to reflect that change in the `main.py` file also (until I implement
environment variables in an upcoming commit).

#### Backend
Requires Python3.9+. Navigate to the `backend` folder and create and activate your virtual environment
(venv recommended), then install the required packages using:
```pip install -Ur requirements/local.txt```

Once requirements are installed, navigate to the `src` folder and run:

`uvicorn main:app --reload`

This will launch the app on port 8000 by default.


#### Frontend
Requires Node.js. Navigate to the `frontend` folder and install the required packages using:

```npm install```

Once packages are installed, run:

```npm start```

This will start the React app on port 3000 by default.

## Using the app

Full list of endpoints and details can be found at
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Example search (you may need to change the query to see some results, since you will receive a different set of random
articles):
[http://127.0.0.1:8000/search/?q=act](http://127.0.0.1:8000/search?query=act)

Example result:
```json
{
    "results":
         {
            "Statue of Cosimo I": 1.6436972762369082,
            "Trihalomethane": 1.4771313555617704,
            "Joseph Henry Morris House": 1.3022414039433408,
            "Neuadd Dwyfor": 1.1306068876621977,
            "Gutierre Vermúdez": 1.0185666732810175,
            "Great Bakersfield Fire of 1889": 1.000698806614099,
            "Eureka Street (novel)": 0.911915592081272,
            "The Real World: San Francisco":0.7130057951771621,
            "Laid Back":0.6889075703961695,
            "Yana Milev":0.3727990368545083
          }
}

```

## Running tests

To run the automated tests locally, navigate to the `backend` directory and simply execute `pytest`
