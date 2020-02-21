import flaskphiid
import unittest
import json

from flask import g, session, Response
from flaskphiid import create_app
from unittest.mock import patch, MagicMock
import flaskphiid.hutchner as hutchner

class hutchnerEndpointTests(unittest.TestCase):

    def setUp(self):
        # creates a test client
        test_config = {'SECRET_KEY':'dev',
                       'TESTING':True,
                       'HUTCHNER_MODEL': "test_resources/simple_crf_ner.pkl"

        }
        self.app = create_app(test_config).test_client()
        # propagate the exceptions to the test client
        self.app.testing = True

        self.INPUT_TEXT = "the quick brown fox jumped over the lazy dog"


    def tearDown(self):
        pass

    def make_json_post_to_endpoint(self, endpoint, dict_to_jsonify):
        return self.app.post(endpoint,
                               data=json.dumps(dict_to_jsonify),
                               content_type='application/json'
                               )


    def test_annotate_no_entity_text(self):
        # sends HTTP GET request to the application
        # on the specified path
        result = self.app.post('/hutchner/annotate/')

        # assert the status code of the response
        self.assertEqual(result.status_code, 400)

    def test_annotate_empty_entity_text(self):
        # sends HTTP GET request to the application
        # on the specified path
        result = self.make_json_post_to_endpoint('/hutchner/annotate/',
                                                 dict())

        # assert the status code of the response
        self.assertEqual(result.status_code, 400)


    @patch('flaskphiid.hutchNERInterface.predict')
    def test_get_entities_happy_case(self, mockHutchNERInterface):
        mockEntityResponse = MagicMock()
        entity_response_json = [{'fox': 'PHI'}, {'dog': 'PHI'}]
        mockEntityResponse.to_json.return_value = entity_response_json
        mockHutchNERInterface.return_value = mockEntityResponse
        expected_result = Response(entity_response_json, mimetype=u'application/json')
        result = hutchner._get_entities(self.INPUT_TEXT, entityTypes="all")

        mockHutchNERInterface.assert_called_with(self.INPUT_TEXT)


if __name__ == '__main__':
    unittest.main()
