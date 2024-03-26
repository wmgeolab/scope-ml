import logging

# logging.basicConfig(level=logging.DEBUG)

from ml_api.ml_algorithms.doc_qa import extract_actors, extract_locations
from ml_api.models.extraction import ExtractedActors, ExtractedLocations

from ml_api.scope_db.crud import get_document, get_sourcing_source, get_sourcing_sources


def extract_locations_test():
    extracted_locations = extract_locations(2)

    for location in extracted_locations.locations:
        print(location)
    # print(extracted_locations)


def get_sourcing_sources_test():
    sources = get_sourcing_sources()

    source = sources[0]
    print(type(source))
    print(type(source.id))
    print(type(sources))
    print(len(sources))


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
