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


## Reflective Response
What unique challenges do you foresee in developing and integrating AI regulatory agents for legal
compliance from a full-stack perspective? How would you address these challenges to make the system
robust and user-friendly?

Your response should reflect your current ideas and we request that you refrain from using GenAI tools for this
section (but feel free to use any other resource). We have included a summary of Norm’s mission below,
which should be helpful as you think through your response.

Mission:
Norm Ai is automating compliance processes, making them more efficient, cost-effective, and accurate than
ever before, while also ensuring democratic guardrails for AI in autonomous roles. By converting complex
regulations into intelligent AI programs, we enable compliance teams to operate with unprecedented speed
and precision. Our vision extends beyond just assisting compliance teams; we aim to enable the integration of
AI agents into daily life, ensuring that AI-driven business processes adhere to legal and societal norms
through adoption of our Regulatory AI agents as oversight. At Norm Ai, we're committed to aligning AI with
public policy, reflecting our society's collective will, and ushering in a new era of regulatory intelligence and
societal-AI alignment.


How I would imagine the technical flow goes:
1. Ingesting laws into deterministic principles and guardrails (PDF Parsing)
2. Making sure that we're always contextualizing the right laws during compliance (RAG), and making sure we apply the right principles at the fringes of compliance.
3. Outlining the discrepancies between in-compliance and out-of-compliance (and/or actioning on fixing out-of-compliance by ourselves)

1. Law ingestion & enforcement
Laws have always been enforced by humans (in-house counsel, judges, police) -- people who understand the nuances and the wording. Converting those into something that a computer can action on is, as far as I know novel. 
LLMs are crucial in this aspect since it's creativity and ability to understand is like a human brain (such that it can understand lossy text and the nuances), but just as self-driving-cars must be better than humans to gain
widespread adoption, so do regulatory agents. Helping the model fully contextualize without hallucination and false-positives/false-negatives would be a difficult problem.

I don't think there's a purely deterministic/algorithmic way of solving this problem. Intuitively it doesn't seem like you can map a law to "if this then that". But breaking these laws down to fully-contextual but small pieces would help the model be more accurate and precise.

2. Norm.Ai's website contains examples of laws that can be enforced by regulatory agents such as the Clean Air Act. For laws such as these, the physical-aspect of laws would be difficult to enforce in an automated fashion. Going to factories to check on 
emissions and making sure cars do not emit more pollution than allowed. In these situations, the manual labor is the more difficult aspect of checking for compliance instead of the information review afterwards. Perhaps the robotics revolution will help us there.

3. Actioning on out-of-compliance.
On a front-end side, making sure the suggestions & edits we've made to any document are fully visible for humans to re-review our work would be an interesting challenge. It'll essentially be like Git! Multiple commits made by the AI to various files, visualizations of the diff, etc.

4. Internationalization
If we expand the scope of "full-stack" we can also think of checking for compliance in laws of different countries, etc. I'm sure there's a lot of US-centric assumptions baked in to our current thinking, and we'd have to expand the scope and system if we were to onboard additional out-of-country users.