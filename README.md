# SCOPE-ML

This repository contains the code for the machine learning backend of the SCOPE project. This currently includes a FastAPI server that provides summarization and question answering services. In the future, this repository may contain web interfaces for interacting with the API in a user friendly way.

## /deployment

Contains all kubernetes related deployment manifests.

## /ml-api

Contains code for the ml-backend api that responds to requests for summarization and question answering from the scope backend.

## /gef-portal-scraper

Contains code for scraping the GEF portal for project data.

## /k8s-autoscaler

Contains code for a FastAPI server that manages the scaling of certain deployments.

## /gef-portal-scraper

Contains code for scraping data from the GEF portal. One script (get_project_ids) gets an updated list of project ids and the other (gef_portal_scraper) downloads any new files using the project ids from step 1.

