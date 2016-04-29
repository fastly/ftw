import unittest
from ftw import util, ruleset, http

class TestModSecurityv2(unittest.TestCase):
    def setUp(self):
        self.yaml_files = util.get_files('test/yaml', 'yaml')
        self.extracted_yaml = util.extract_yaml(self.yaml_files)
        self.ruleset = ruleset.Ruleset(self.extracted_yaml)
        for test in self.ruleset.tests:
            for stage in test.stages:
                # provide request parameters to web parser
                http_ua = http.HttpUA(stage.input)
                # issue web request
                http_ua.send_request()
                # check response and assert
        print 'Setting up!'

    def tearDown(self):
        print 'Tearing down!'

    def test_c(self):
        assert len(self.extracted_yaml) > 0

    def test_yaml(self):
        pass 
