import os
import re
from enum import Enum
from typing import List


class DocumentType(str, Enum):
    CEO_ENDORSEMENT = "CEO Endorsement"
    REVIEW_SHEET_CEO_ENDORSEMENT = "Review Sheet for CEO Endorsement"
    PROJECT_IMPLEMENTATION_REPORT = "Project Implementation Report (PIR)"
    PROJECT_IDENTIFICATION_FORM = "Project Identification Form (PIF)"
    REVIEW_SHEET_PIF = "Review Sheet for PIF"
    STAP_REVIEW = "STAP Review"
    AGENCY_PROJECT_DOCUMENT = "Agency Project Document"
    FSP_PIF_DOCUMENT = "FSP PIF Document"
    FSP_CEO_ENDORSEMENT_DOCUMENT = "FSP CEO Endorsement Document"
    MSP_CEO_APPROVAL_DOCUMENT = "MSP CEO Approval Document"
    MSP_PIF_DOCUMENT = "MSP PIF Document"
    CEO_PIF_CLEARANCE_LETTER = "CEO PIF Clearance Letter"
    CEO_ENDORSEMENT_LETTER = "CEO Endorsement Letter"
    PPG_APPROVAL_LETTER = "PPG Approval Letter"
    MIDTERM_REVIEW = "Midterm Review (MTR)"
    CHILD_FSP_CEO_ENDORSEMENT_DOCUMENT = "Child FSP CEO Endorsement Document"
    COUNCIL_NOTIFICATION_LETTER = "Council Notification Letter"
    PPG_DOCUMENT = "PPG Document"
    ANNEXES_APPENDIXES = "Annexes/Appendixes to Project Documents"
    AGENCY_RESPONSE_MATRIX = "Agency Response Matrix"
    UNKNOWN = "Unknown"


def extract_and_identify_filename(filename):
    original_filename = extract_original_filename(filename)
    return identify_document_type(original_filename)


def select_doc_types_for_project(project_id, data_dir: str = "../data/gef-7/"):
    return select_document_types(get_doc_types_for_project(project_id, data_dir))


def get_doc_types_for_project(project_id, data_dir):
    doc_types: List[DocumentType] = []
    for filename in os.listdir(data_dir + str(project_id)):
        doc_type = extract_and_identify_filename(filename)
        doc_types += [doc_type]
    return list(set(doc_types))


def select_document_types(available_types: List[DocumentType]) -> List[DocumentType]:
    selected_types = []

    # Priority order based on the email
    priority_order = [
        # DocumentType.TERMINAL_EVALUATION,
        DocumentType.MIDTERM_REVIEW,
        DocumentType.PROJECT_IMPLEMENTATION_REPORT,
        DocumentType.CEO_ENDORSEMENT,
    ]

    # First, check for the highest priority document available
    for doc_type in priority_order:
        if doc_type in available_types:
            selected_types.append(doc_type)
            break

    # If we selected a PIR, also include CEO Endorsement if available
    if (
        selected_types
        and selected_types[0] == DocumentType.PROJECT_IMPLEMENTATION_REPORT
    ):
        if DocumentType.CEO_ENDORSEMENT in available_types:
            selected_types.append(DocumentType.CEO_ENDORSEMENT)

    # If we only have CEO Endorsement, include it
    if not selected_types and DocumentType.CEO_ENDORSEMENT in available_types:
        selected_types.append(DocumentType.CEO_ENDORSEMENT)

    # Include any other available monitoring or evaluation reports
    for doc_type in priority_order:
        if doc_type in available_types and doc_type not in selected_types:
            selected_types.append(doc_type)

    return selected_types


def extract_original_filename(filename):
    """
    Extract the original name of the file as downloaded from GEF.

    This function uses a regular expression to match a specific pattern in the filename.
    The pattern is expected to be in the format "p<digits>_doc<digits>__<original_filename>".
    If the filename matches this pattern, the function extracts and returns the original filename.
    If the filename does not match the pattern, the function returns the original filename as is.

    Args:
        filename (str): The name of the file to be processed.

    Returns:
        str: The extracted original filename if the pattern matches, otherwise the input filename.
    """
    """Extract the original name of the file as downloaded from GEF"""

    pattern = (
        r"^p\d+_doc\d+__(.+)$"  # captures characters after the last double underscore
    )
    match = re.match(pattern, filename)

    if match:
        return match.group(1)
    else:
        return filename


def identify_document_type(filename: str) -> DocumentType:
    patterns = [
        (r"_CEOEndorsement\.pdf$", DocumentType.CEO_ENDORSEMENT),
        (
            r"_ReviewSheet_CEOEndorsement\.pdf$",
            DocumentType.REVIEW_SHEET_CEO_ENDORSEMENT,
        ),
        (
            r"^ProjectImplementationReportPIR_",
            DocumentType.PROJECT_IMPLEMENTATION_REPORT,
        ),
        (r"_PIF\.pdf$", DocumentType.PROJECT_IDENTIFICATION_FORM),
        (r"_ReviewSheet_PIF\.pdf$", DocumentType.REVIEW_SHEET_PIF),
        (r"^STAPreview_|_STAPReview\.pdf$", DocumentType.STAP_REVIEW),
        (r"^Agencyprojectdocument_", DocumentType.AGENCY_PROJECT_DOCUMENT),
        (r"^FSPPIFdocument_", DocumentType.FSP_PIF_DOCUMENT),
        (r"^FSPCEOEndorsementdocument_", DocumentType.FSP_CEO_ENDORSEMENT_DOCUMENT),
        (r"^MSPCEOApprovaldocument_", DocumentType.MSP_CEO_APPROVAL_DOCUMENT),
        (r"^MSPPIFdocument_", DocumentType.MSP_PIF_DOCUMENT),
        (r"^CEOPIFClearanceLetter_", DocumentType.CEO_PIF_CLEARANCE_LETTER),
        (r"^CEOEndorsementLetter_", DocumentType.CEO_ENDORSEMENT_LETTER),
        (r"^PPGApprovalLetter_", DocumentType.PPG_APPROVAL_LETTER),
        (r"^MidtermReviewMTR_", DocumentType.MIDTERM_REVIEW),
        (
            r"^ChildFSPCEOEndorsementdocument_",
            DocumentType.CHILD_FSP_CEO_ENDORSEMENT_DOCUMENT,
        ),
        (
            r"^CouncilNotificationLetterof(ChildProjectunderaProgramforreview|CEOEndorsementofaFSP)_",
            DocumentType.COUNCIL_NOTIFICATION_LETTER,
        ),
        (r"^PPGdocument_", DocumentType.PPG_DOCUMENT),
        (r"^Annexesappendixestotheprojectdocuments_", DocumentType.ANNEXES_APPENDIXES),
        (r"^Agencyresponsematrix_", DocumentType.AGENCY_RESPONSE_MATRIX),
    ]

    for pattern, doc_type in patterns:
        if re.search(pattern, filename):
            return doc_type

    return DocumentType.UNKNOWN
