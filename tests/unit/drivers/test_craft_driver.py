from typing import Dict
import numpy as np
from jina.drivers.craft import CraftDriver
from jina.executors.crafters import BaseCrafter
from jina.drivers.helper import array2pb
from jina.proto import jina_pb2
from tests import JinaTestCase


class MockCrafter(BaseCrafter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_keys = {'text'}

    def craft(self, text: str, *args, **kwargs) -> Dict:
        if text == 'valid':
            return {'blob': np.array([0.0, 0.0, 0.0]), 'weight': 10}
        else:
            return {'non_existing_key': 1}


class SimpleCraftDriver(CraftDriver):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def exec_fn(self):
        return self._exec_fn


def create_documents_to_craft():
    doc1 = jina_pb2.Document()
    doc1.id = 1
    doc1.text = 'valid'
    doc2 = jina_pb2.Document()
    doc2.id = 2
    doc2.text = 'invalid'
    return [doc1, doc2]


class CraftDriverTestCase(JinaTestCase):

    def test_craft_driver(self):
        docs = create_documents_to_craft()
        driver = SimpleCraftDriver()
        executor = MockCrafter()
        driver.attach(executor=executor, pea=None)
        driver._apply(docs[0])
        self.assertEqual(docs[0].blob, array2pb(np.array([0.0, 0.0, 0.0])))
        self.assertEqual(docs[0].weight, 10)
        with self.assertRaises(AttributeError) as error:
            driver._apply(docs[1])
        self.assertEqual(error.exception.__str__(), '\'Document\' object has no attribute \'non_existing_key\'')
