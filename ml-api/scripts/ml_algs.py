import csv
import logging
import os

from api.ml_algorithms.extract import doc_extract_actors, doc_extract_locations
from api.models.extraction import (
    Actor,
    ExtractedActors,
    ExtractedLocations,
    Location,
)
from api.scope_db.crud import get_document, get_sourcing_source, get_sourcing_sources

logging.basicConfig(level=logging.INFO)


def extract_locations_test(doc_id: int = 2) -> ExtractedLocations:
    extracted_locations = doc_extract_locations(doc_id)

    return extracted_locations


def extract_actors_test(doc_id: int = 2) -> ExtractedActors:
    extracted_actors = doc_extract_actors(doc_id)

    return extracted_actors


def get_sourcing_sources_test():
    return get_sourcing_sources()


def get_sourcing_source_test(doc_id: int = 1):
    source = get_sourcing_source(doc_id)
    print(type(source))
    # print(source.source_text)
    print(source.source_date)


def main():
    locs = extract_locations_test()
    acts = extract_actors_test()

    # add to csv sample_locations.csv and sample_actors.csv in current dir
    # This should append to the csv if it already exists

    with open("sample_locations.csv", "a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=Location.__fields__.keys())
        # If the file is empty, write the header
        if os.stat("sample_locations.csv").st_size == 0:
            writer.writeheader()
        for location in locs.locations:
            writer.writerow(location.dict())

    with open("sample_actors.csv", "a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=Actor.__fields__.keys())
        # If the file is empty, write the header
        if os.stat("sample_actors.csv").st_size == 0:
            writer.writeheader()
        for actor in acts.actors:
            writer.writerow(actor.dict())


if __name__ == "__main__":
    main()
