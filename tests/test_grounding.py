import unittest, json
from pathlib import Path
from src.retriever import retrieve, evaluate
from src.schema_validator import validate
class GroundingChecks(unittest.TestCase):
    def setUp(self): self.corpus=json.loads(Path('data/mil_std_excerpts.json').read_text())
    def test_abstention(self): self.assertTrue(retrieve('quantum penguins',self.corpus)['abstained'])
    def test_forged_citation_rejected(self):
        response=retrieve('sensor calibration',self.corpus); response['citations'][0]['quote']='fabricated'
        with self.assertRaises(ValueError): validate(response,self.corpus)
    def test_known_cases(self):
        cases=json.loads(Path('data/evaluation_cases.json').read_text())
        self.assertEqual(evaluate(self.corpus,cases)['accuracy'],1)
