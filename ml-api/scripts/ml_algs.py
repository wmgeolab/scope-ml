import logging

from ml_api.ml_algorithms.doc_qa import doc_extract_actors, doc_extract_locations
from ml_api.models.extraction import ExtractedActors, ExtractedLocations
from ml_api.scope_db.crud import get_document, get_sourcing_source, get_sourcing_sources

logging.basicConfig(level=logging.INFO)


def extract_locations_test():
    extracted_locations = doc_extract_locations(2)

    for location in extracted_locations.locations:
        print(location)


def get_sourcing_sources_test():
    sources = get_sourcing_sources()


def get_sourcing_source_test():
    source = get_sourcing_source(1)
    print(type(source))
    # print(source.source_text)
    print(source.source_date)


def main():
    extract_locations_test()
    # get_sourcing_sources_test()


if __name__ == "__main__":
    main()
