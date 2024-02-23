from llama_index.core import PromptTemplate

SUMMARY_TEMPLATE = PromptTemplate(
    """
    {document_text}
    
    Provide a comprehensive summary of the above document. The summary should be no longer than 500 words.
    """
)
