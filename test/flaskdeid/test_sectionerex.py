import flaskdeid
import unittest
import json
import os
import re
from contextlib import contextmanager
from flask import g, session, Response, appcontext_pushed
from flaskdeid import create_app
from unittest.mock import patch
import flaskdeid.sectionerex as sectionerex


class SectionerexEndpointTests(unittest.TestCase):

    def setUp(self):
        # creates a test client
        self.TEST_RESOURCE_PATH = os.path.join(os.path.split(__file__)[0], "test_resources")
        test_config = {'SECRET_KEY':'dev',
                       'TESTING':True,
                       'SECTIONER_MODEL_LOC': self.TEST_RESOURCE_PATH

        }
        self.app = create_app(test_config).test_client()
        # propagate the exceptions to the test client
        self.app.testing = True

        self.INPUT_TEXT = "the quick brown fox jumped over the lazy dog"
        self.DEFAULT_RULES_DICT = {'default':
                                       [('Header', re.compile('^ H*', re.IGNORECASE|re.MULTILINE)),
                                        ],
                                   'other':
                                   [('Allergies', re.compile('Allergies', re.IGNORECASE|re.MULTILINE)),
                                    ]
                                   }


    def tearDown(self):
        pass


    @contextmanager
    def sectioner_set(app, user):
        def handler(sender, **kwargs):
            g.user = user

        with appcontext_pushed.connected_to(handler, app):
            yield


    def load_test_rules(self):
        # Test labeling with standard rules
        custom_rpath = os.path.join(os.path.split(__file__)[0], "test_resources")

        rules = sectionerex.load_rules(self.TEST_RESOURCE_PATH)

        return rules


    def make_json_post_to_endpoint(self, endpoint, dict_to_jsonify):
        return self.app.post(endpoint,
                               data=json.dumps(dict_to_jsonify),
                               content_type='application/json'
                               )


    @patch('sectionerex.sectionerex.load_rules')
    def setup_sectioner_results(self, mockSectionerEx):
        mockSectionerEx.return_value = self.DEFAULT_RULES_DICT

        return mockSectionerEx


    def test_annotate_no_entity_text(self):
        # sends HTTP GET request to the application
        # on the specified path
        result = self.app.post('/sectionerex/')

        # assert the status code of the response
        self.assertEqual(result.status_code, 400)


    @patch(sectionerex.__name__+'.sectionerex.load_rules')
    def test_sectioner_specific_endpoint(self, mockSectionerExLoadRules):
        mockSectionerExLoadRules.return_value = self.DEFAULT_RULES_DICT
        result = self.make_json_post_to_endpoint('/sectionerex/other',
                                                 {"extract_text": "Header\n Allergies: None "})

        mockSectionerExLoadRules.assert_called_with(dirpath=self.TEST_RESOURCE_PATH)
        # assert the status code of the response
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json, [{'end': 8, 'section': 'Header', 'start': 7, 'text': ' '}, {'end': 17, 'section': 'Allergies', 'start': 8, 'text': 'Allergies'}])


    @patch(sectionerex.__name__ + '.sectionerex.load_rules')
    def test_sectioner_open_endpoint(self, mockSectionerExLoadRules):
        mockSectionerExLoadRules.return_value = self.DEFAULT_RULES_DICT
        result = self.make_json_post_to_endpoint('/sectionerex/',
                                                 {"extract_text": "Header\n Allergies: None "})

        mockSectionerExLoadRules.assert_called_with(dirpath=self.TEST_RESOURCE_PATH)
        # assert the status code of the response
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json, [{'end': 8, 'section': 'Header', 'text': ' ', 'start': 7}])


    @patch(sectionerex.__name__ + '.sectionerex.load_rules')
    def test_sectioner_unsupported_endpoint(self, mockSectionerExLoadRules):
        mockSectionerExLoadRules.return_value = self.DEFAULT_RULES_DICT
        result = self.make_json_post_to_endpoint('/sectionerex/allaboutcats',
                                                 {"extract_text": "Header\n Allergies: None "})

        mockSectionerExLoadRules.assert_called_with(dirpath=self.TEST_RESOURCE_PATH)
        self.assertEqual(result.status_code, 400)



if __name__ == '__main__':
    unittest.main()