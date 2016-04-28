import re
class Output():
    """
    This class holds the expected output from a corresponding FTW HTTP Input
    We are stricter in this definition by requiring at least one of status,
    html_contains or log_contains
    """
    def __init__(self, output_dict):
        self.STATUS = 'status'
        self.LOG = 'log_contains'
        self.HTML = 'html_contains'
        self.output_dict = output_dict
        self.status = output_dict[self.STATUS] \
            if output_dict.has_key(self.STATUS) else None
        self.html_contains = self.process_regex(self.HTML) 
        self.log_contains = self.process_regex(self.LOG)
        if self.status == None and self.html_contains == None \
            and self.log_contains == None:
            raise ValueError('Need at least one status, html_contains or log_contains')

    def process_regex(self, key):
        """
        Extract the value of key from dictionary if available
        and process it as a python regex
        """
        if self.output_dict.has_key(key):
            return re.compile(self.output_dict[key])    
        else:
            return None

class Input():
    """
    This class holds the data associated with an HTTP Input request in FTW
    """
    def __init__(self, raw_request = '',
                    protocol = 'http',
                    dest_addr = 'localhost',
                    port = 80,
                    method = 'GET',
                    uri = '/',
                    version = 'HTTP/1.1',
                    headers = {},
                    data = '',
                    status = 200,
                    save_cookie = False,
                    ):
        self.raw_request = raw_request
        self.protocol = protocol
        self.port = port
        self.method = method
        self.uri = uri
        self.version = version
        self.headers = headers
        self.data = data
        self.status = status
        self.save_cookie = save_cookie

class Stage():
    """
    This class holds information about 1 stage in a test, which contains
    1 input and 1 output
    """
    def __init__(self, stage_dict):
        self.stage_dict = stage_dict
        self.input = Input(**stage_dict['input'])
        self.output = Output(stage_dict['output'])
        
class Test():
    """
    This class holds information for 1 test and potentially many stages
    """
    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.stages = self.build_stages()

    def build_stages(self):
        """
        Processes and loads an array of stages from the test dictionary
        """
        return map(lambda stage_dict: Stage(stage_dict['stage']), \
                    self.test_dict['stages'])
        
class Ruleset():
    """
    This class holds test and stage information from a YAML test file
    These YAML files are used to test the OWASP/Modsec CRSv3 rules 
    """
    def __init__(self, yaml_file):
        self.yaml_file = yaml_file
        self.meta = yaml_file['meta'] 
        self.author = self.meta['author']
        self.description = self.meta['description']
        self.enabled = self.meta['enabled']
        self.tests = self.extract_tests() if self.enabled else []

    def extract_tests(self):
        """
        Processes a loaded YAML document and creates test objects based on input 
        """
        try:
            tests = map(lambda test_dict: Test(test_dict), \
                             self.yaml_file['tests'])
            return tests
        except Exception as e:
            raise Exception('Caught error. Message: %s on test with metadata: %s' % (str(e), str(self.meta)))
