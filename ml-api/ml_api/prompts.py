from llama_index.core import PromptTemplate

SUMMARY_TEMPLATE = PromptTemplate(
    """
    {document_text}
    
    Provide a comprehensive summary of the above document. The summary should be no longer than 500 words.
    """
)

QA_TEMPLATE = PromptTemplate(
    """
    {document_text}
    
    Answer the following question: {question}
    """
)

EXTRACT_LOCATIONS_TEMPLATE = PromptTemplate(
    """
    {document_text}
    
    Extract the locations mentioned in the above document.
    """
)

EXTRACT_ACTORS_TEMPLATE = PromptTemplate(
    """
    {document_text}
    
    Extract the actors mentioned in the above document.
    """
)
