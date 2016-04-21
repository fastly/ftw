import unittest
from ftw import util

class TestModSecurityv2(unittest.TestCase):
    def setUp(self):
        self.yaml_files = util.get_files('test/yaml', 'yaml')
        self.extracted_yaml = util.extract_yaml(self.yaml_files)
        self.tests = util.extract_tests(self.extracted_yaml)
        # instantiate web parser library thing
        # for each test
            # provide request parameters to web parser
            # issue web request
            # check response and assert
        print 'Setting up!'

    def tearDown(self):
        print 'Tearing down!'

    def test_c(self):
        assert len(self.extracted_yaml) > 0

    def test_yaml(self):
        pass 
