# llm-api

# Description
The repository invovles the FastAPI backend for interacting with Sagemaker endpoints for LLMs. We can create, stop, delete and call the endpoints.
There's a websocket endpoint for listening the creation status of endpoints.

# Local development
## Prerequisites
- Python 3.11
- Docker

## Start app
You can start the app in with or without Docker.
### Without Docker
- At the project's root folder, run 
```
pip install -r requirements/dev.txt
```
```commandline
export DEPLOY_ENV=local && uvicorn src.main:app --reload
```

### With Docker
- Build image: run `docker build -t <image_name> -f Dockerfile-local .` at the root folder.
- Start the container in the interactive mode: 
```
docker run -it --rm -v ~/.aws:/root/.aws  --name <container_name> -p 80:80 <image_name>
```

## Call from frontend service
You may encounter the CORS error when calling the endpoints from a frontend application locally, for example from `localhost:3000`. Add this code snippet in the `main.py` file of this repo.
```commandline
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Run tests and coverage
- Install `pytest` and `coverage` packages
- To run tests only, use `pytest` at the root
- To run tests with cover, use 
```commandline
coverage run --source=./src -m pytest
```
the option `source` limits the folders to be scanned for coverage. Execute `coverage html`and go to the generated htmlcov folder inside the repository and find `index.html` to see details.

