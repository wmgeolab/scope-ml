"""
This service is responsible for ingesting data (pdf, docx, etc) into the Qdrant database.

This includes parsing the raw document to text, chunking the text with metadata,
and indexing the chunks into the Qdrant database to be used in inference.
"""