from ..ml_api.ml_algorithms.doc_qa import extract_actors, extract_locations
from ..ml_api.models.extraction import ExtractedActors, ExtractedLocations


def test_extract_locations():
    """Test that the extract_locations function runs without errors and returns an ExtractedLocations object."""
    extracted_locations = extract_locations(0)
    assert isinstance(extracted_locations, ExtractedLocations)


def test_extract_actors():
    """Test that the extract_actors function runs without errors and returns an ExtractedActors object."""
    extracted_actors = extract_actors(0)
    assert isinstance(extracted_actors, ExtractedActors)
