This repository contains a client and server codebase. 

## Server Repository:

This codebase contains a list of laws (`docs/laws.pdf`) taken from the fictional series “Game of Thrones” (randomly pulled from a wiki fandom site... unfortunately knowledge of the series does not provide an edge on this assignment). Your task is to implement a new service (described in take home exercise document) and provide access to that service via a FastAPI endpoint running in a docker container. Please replace this readme with the steps required to run your app.

## Client Repository 

In the `frontend` folder you'll find a light NextJS app with it's own README including instructions to run. Your task here is to build a minimal client experience that utilizes the service build in part 1.

## SETUP
1. Have all necessary prequisites installed (python, docker)
2. `docker build -t norm-takehome` to build the Docker image.
3. `docker run -p 8080:80 -e OPENAI_API_KEY=$OPENAI_API_KEY norm-takehome` to run the Docker container, with the server running on port 8080. Remember to properly set the OPENAI env variable.
4. Query the service-endpoint. e.g. via curl: `curl -X POST http://localhost:8080/v1/laws/game_of_thrones -H "Content-Type: application/json" -d '{"query": "What happens if I steal?"}'`


## Decisions/Assumptions/Design
- Document parsing
1. There are certain sections of PDF documents that won't be relevant for parsing laws. For the current example, I chose a simple y-coord based filtering.
2. There's various heuristics across documents to infer its structure. For this exercise, I only used regex/basic string-parsing. We definitely go more advanced here for things to be more robust.
3. It appears that (as the exercise stated) the Document/Node classes of llama-index will handle these parsing steps for us. We should try to rely on them if they provide the robustness we're looking for as per above.

- Querying
1. The citation structure from `CitationQueryEngine` is embedded in the text itself. This is unstructured and brittle -- we should create a better QueryEngine to return citations in a more structured format.

- API Service
1. We're currently assuming that the laws that can be served are ~static (by exposing a static endpoint per law). We can change this and make the law a required field in the body of a request, for example.
2. In practice, we'd have a vector-db of some sort set up with these parsed laws instead of re-parsing them every single time. That way this is a service-front just to serve requests, not to parse documents.