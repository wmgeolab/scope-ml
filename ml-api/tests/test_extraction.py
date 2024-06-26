import pytest
from ml_api.ml_algorithms.extract import doc_extract_actors, doc_extract_locations
from ml_api.models.extraction import ExtractedActors, ExtractedLocations

from .config import TestConfig


@pytest.mark.parametrize("document_id", TestConfig.VALID_DOCUMENT_IDS)
def test_extract_locations(document_id: int):
    """Test that the extract_locations function runs without errors and returns an ExtractedLocations object."""
    extracted_locations = doc_extract_locations(document_id)
    assert isinstance(extracted_locations, ExtractedLocations)
    assert extracted_locations.locations != []


@pytest.mark.parametrize("document_id", TestConfig.VALID_DOCUMENT_IDS)
def test_extract_actors(document_id: int):
    """Test that the extract_actors function runs without errors and returns an ExtractedActors object."""
    extracted_actors = doc_extract_actors(document_id)
    assert isinstance(extracted_actors, ExtractedActors)
    assert extracted_actors.actors != []
