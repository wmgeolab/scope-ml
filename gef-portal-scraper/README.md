# gef-portal-scraper

Downloads publicly available documents from the Global Environment Facility (gef) website.

## get_project_ids

Creates a json file containing all valid gef project ids. A similar list can be downloaded in csv format directly from the gef's website (https://www.thegef.org/projects-operations/database).

## gef_portal_scraper

Uses the list of project ids to scrape the gef database, downloading documents associated with each project. A local SQLite database records which documents have already been downloaded and can be skipped on subsequent runs.

NOTE: The actual documents (pdfs/docs) are downloaded to a seperate directory structure, which could theoretically become desynced from the SQLite database. 

## document_db_manager

Contains methods for interacting with the SQLite database.


# How to Run these Scripts

It is recommended to run these scripts as containers using docker.

## Locally

From the gef-portal-scraper directory, build the image using the Dockerfile and name it gef_scraper.
```
docker build -t gef_scraper .
```

Run the gef_scraper image linking the local data directory to the container's data directory (this is where the documents and SQLite database will be stored)
```
docker run -v "$(pwd)/data:/app/data" gef_scraper
```

## On the Cluster

Github Actions automatically builds a new image after each commit. The yml files in the deployment/scraper folder define which image to pull and how it should be run.

```
kubectl create -f gef-scraper.yml -n scope-dsmr
```

# TODO

Ideally, the scraper would be run on a regular interval to stay updated with new documents. Using a [Kubernetes CronJob](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/) would make sense but appears to be currently permission blocked on the cluster.
