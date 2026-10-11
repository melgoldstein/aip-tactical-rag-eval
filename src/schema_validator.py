"""Strict response shape and exact source-support validation."""
from typing import TypedDict
from pathlib import Path
import json
from jsonschema import Draft202012Validator
SCHEMA = json.loads((Path(__file__).resolve().parents[1]/"data/response.schema.json").read_text())
class Citation(TypedDict):
    document_id: str
    quote: str
class RetrievalResponse(TypedDict):
    query: str
    answer: str
    citations: list[Citation]
    abstained: bool
def validate(response: dict[str,object], corpus: list[dict[str,str]]) -> None:
    if list(Draft202012Validator(SCHEMA).iter_errors(response)):
        raise ValueError('JSON schema validation failed')
    if set(response) != {'query','answer','citations','abstained'}:
        raise ValueError('Unexpected response schema')
    if not isinstance(response['query'],str) or not isinstance(response['answer'],str) or type(response['abstained']) is not bool or not isinstance(response['citations'],list):
        raise ValueError('Invalid response types')
    documents={entry['id']:entry['text'] for entry in corpus}
    for citation in response['citations']:
        if not isinstance(citation,dict) or set(citation)!={'document_id','quote'} or not all(isinstance(value,str) for value in citation.values()):
            raise ValueError('Invalid citation schema')
        if not citation['quote'] or citation['document_id'] not in documents or citation['quote'] not in documents[citation['document_id']]:
            raise ValueError('Unsupported citation')
    if response['abstained']:
        if response['answer'] or response['citations']: raise ValueError('Abstention carries an answer')
    elif not response['citations'] or response['answer'] != ' '.join(c['quote'] for c in response['citations']):
        raise ValueError('Answer is not grounded in cited text')
