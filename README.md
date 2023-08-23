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
### Environment variables
Environment variables will need to be set up for the app to run. You can do this by copying the `.env.template` to a
file called `.env` in the `envs` directory, and then setting the values as required.

The `POSTGRES_HOST` variable will need to be set to `db` if you are running the app using Docker, or to `localhost` if
you are running the app locally. To run the app locally, you will also need to set the `POSTGRES_USER` and
`POSTGRES_PASSWORD` variables to the username and password of your Postgres user.

To set variables locally, you can use Dotenv to load the variables from the `.env` file. To do this, install Dotenv
using `pip install python-dotenv`, then add the following to the top of the `main.py` file or `settings.py` file:

```python
from dotenv import load_dotenv

load_dotenv("../envs/.env")
```

Alternatively you can manually set the variables in your terminal before running the app, e.g.:

```bash
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=password
...
```

or in Windows:

```bash
set POSTGRES_USER=postgres
set POSTGRES_PASSWORD=password
...
```

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

Once set up, you can use whatever database, user & password you like (you will need to set these in the `.env` file or
manually, see above). With your Postgres instance running, you can create the tables by running the
Alembic migrations. Navigate to the `backend` folder and run:

```alembic upgrade head```

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

The frontend React app will show a list of the random articles that have been fetched from Wikipedia.
For now, you can't search for relevant text to the articles that are displayed on the frontend (since I have not yet
added a search term input field), but the logic has been implemented to facilitate this which highlights relevant
articles. You can click then click on a highlighted article to view it in full on Wikipedia. Search input to be added in
an upcoming commit.

Full list of endpoints and details can be found at
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Example search (you may need to change the query to see some results, since you will receive a different set of random
articles):
[http://127.0.0.1:8000/search/?query=act](http://127.0.0.1:8000/search?query=act)

Example result:
```json
{
    "results":
         [
           {"title": "Statue of Cosimo I", "ranking": 1.6436972762369082},
           {"title": "Trihalomethane", "ranking": 1.4771313555617704},
           {"title": "Joseph Henry Morris House", "ranking": 1.3022414039433408},
           {"title": "Neuadd Dwyfor", "ranking": 1.1306068876621977},
           {"title": "Gutierre Vermúdez", "ranking": 1.0185666732810175},
           {"title": "Great Bakersfield Fire of 1889", "ranking": 1.000698806614099},
           {"title": "Eureka Street (novel)", "ranking": 0.911915592081272},
           {"title": "The Real World: San Francisco", "ranking": 0.7130057951771621},
           {"title": "Laid Back", "ranking": 0.6889075703961695},
           {"title": "Yana Milev", "ranking": 0.3727990368545083}
         ]
}

```

## Running tests

To run the automated tests locally, navigate to the `backend` directory and install the BE project as an editable
dependency:

```pip install -e .```

Ensure you have the test requirements installed:

```pip install -Ur requirements/test.txt```

Then simply execute `pytest`.
