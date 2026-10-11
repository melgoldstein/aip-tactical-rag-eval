"""Evaluate a deterministic, abstaining retrieval baseline."""
import json, math, re, time, logging
from pathlib import Path
from src.schema_validator import RetrievalResponse, validate
STOP={'the','a','an','and','for','of','is','what','how','to','in'}
def tokens(text: str) -> set[str]:
    return set(re.findall(r'[a-z0-9]+',text.lower()))-STOP
def retrieve(query: str, corpus: list[dict[str,str]]) -> RetrievalResponse:
    query_terms=tokens(query); ranked=[]
    for document in corpus:
        overlap=query_terms & tokens(document['text'])
        score=sum(math.log((len(corpus)+1)/(1+sum(term in tokens(entry['text']) for entry in corpus)))+1 for term in overlap)
        ranked.append((score,document['id'],document['text']))
    ranked.sort(key=lambda item:(-item[0],item[1]))
    supported=bool(ranked and ranked[0][0]>0)
    response: RetrievalResponse={'query':query,'answer':ranked[0][2] if supported else '', 'citations':[{'document_id':ranked[0][1],'quote':ranked[0][2]}] if supported else [],'abstained':not supported}
    validate(response,corpus); return response
def evaluate(corpus: list[dict[str,str]], cases: list[dict[str,str|None]]) -> dict[str,object]:
    latencies=[]; records=[]
    for case in cases:
        start=time.perf_counter_ns(); response=retrieve(str(case['query']),corpus)
        latencies.append((time.perf_counter_ns()-start)/1e6)
        actual=response['citations'][0]['document_id'] if response['citations'] else None
        records.append({'query':case['query'],'expected':case['expected'],'actual':actual,'passed':actual==case['expected'],'response':response})
    ordered=sorted(latencies)
    return {'cases':records,'accuracy':sum(r['passed'] for r in records)/len(records),'latency_ms':{'p50':ordered[math.ceil(.5*len(ordered))-1],'p95':ordered[math.ceil(.95*len(ordered))-1]},'workflow':'AIP retrieval validation staging; synthetic corpus'}
if __name__=='__main__':
    corpus=json.loads(Path('data/mil_std_excerpts.json').read_text())
    cases=json.loads(Path('data/evaluation_cases.json').read_text())
    result=evaluate(corpus,cases); Path('artifacts').mkdir(exist_ok=True)
    Path('artifacts/evaluation.json').write_text(json.dumps(result,indent=2)+'\n')
    logging.basicConfig(level=logging.INFO); logging.info('Retrieval accuracy %.3f',result['accuracy'])
