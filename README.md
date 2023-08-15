# wikipedia-search

Search a random selection of Wikipedia articles.

### Running the app
#### Docker (recommended)
In the root directory of the project, run:
```docker-compose up --build```

#### Locally
Requires Python3.9+. Package requirements can be found in `requirements/local.txt`. 

Activate your virtual environment of choice and then install the dependencies using:
```pip install -Ur requirements/local.txt```

Once requirements are installed, navigate to the `src` folder and run:

`uvicorn main:app --reload`

The Docker or the local instructions will launch the application on port 8000 by default. On launch the app will fetch 
200 random articles from the Wikipedia API and index them in an inverted index. You can then search for terms and the 
app will return the relevant article titles from those fetched, as ranked by a 
[BM25 ranking algorithm](https://en.wikipedia.org/wiki/Okapi_BM25).

Full list of endpoints and details can be found at 
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Example search (you may need to change the query to see some results):
[http://127.0.0.1:8000/search/?q=act](http://127.0.0.1:8000/search/?q=act)

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

### Running tests

To run the automated tests, navigate to the `src` directory and simply execute `pytest`