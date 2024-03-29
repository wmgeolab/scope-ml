from llama_index.core import PromptTemplate

SUMMARY_TEMPLATE = PromptTemplate(
    """
    {document_text}
    
    Provide a comprehensive summary of the above document. The summary should be no longer than 500 words.
    """
)

QA_TEMPLATE = PromptTemplate(
    """
    Use the following context to answer the question below.
    
    --- CONTEXT START ---
    {document_text}
        
    --- CONTEXT END ---    
    
    
    Answer the following question: {question}
    """
)

EXTRACT_LOCATIONS_TEMPLATE = PromptTemplate(
    """
    {document_text}
    
    Extract the locations mentioned in the above document. Respond in in the requested JSON format. You do not need to escape underscores in strings.
    """
)

EXTRACT_ACTORS_TEMPLATE = PromptTemplate(
    """
    Extract the actors mentioned in the below document.
    
    {document_text}
        
    Respond in in the requested JSON format. You do not need to escape underscores in strings. Be strict about the format of the response.
    """
)
