class Output():
    """
    This class holds the expected output from a corresponding FTW HTTP Input
    """
    def __init__(self, output_dict):
        pass

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
        self.output = Output(**stage_dict['output'])
        import pdb; pdb.set_trace()
        
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
        self.stages = map(lambda stage_dict: Stage(stage_dict['stage']), \
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
        print self.enabled
        self.tests = self.extract_tests() if self.enabled else []

    def extract_tests(self):
        """
        Processes a loaded YAML document and creates test objects based on input 
        """
        print 'in extract tests'
        self.tests = map(lambda test_dict: Test(test_dict), \
                            self.yaml_file['tests'])
