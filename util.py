import glob
import yaml
import syslog

def get_files(directory,extension): 
    """
    Take a directory and an extension and return the files that match the extension
    """
    return glob.glob('%s/*.%s' % (directory,extension))

def extract_yaml(yaml_files):
    """
    Take a list of yaml_files and load them to return back to the testing program
    """
    loaded_yaml = []
    for yaml_file in yaml_files:
        try:
            with open(yaml_file, 'r') as fd:
                loaded_yaml.append(yaml.safe_load(fd)) 
        except IOError as e:     
            print 'Error reading file %s' % yaml_file 
            raise e
        except yaml.YAMLError as e:
            print 'Error parsing file %s' % yaml_file
            raise e
        except Error as e:
            print 'General error'
            raise e
    return loaded_yaml[0]
        
def extract_tests(doc):
    """
    Extracts the tests out of the yaml file
    YAML is loaded as a list, so access the 0th element for the test dict,
    then iterate through and load tests
    """
    myTests = {}
    # Iterate over the different 'named tests' (AKA YAML sections)
    for section, tests in doc.iteritems():
        # Check if our section exists in myTests, if not add it
        if section not in myTests.keys():
            myTests[section] = []
        # Within each YAML section look at each 'test'
        for test in tests:
            ourTest = test['test']
            testData = []
            metaData = {}
            skipTest = False
            for transactions in ourTest:
                # See if we have an input transaction or input
                if 'input' in transactions.keys():
                    inputTestValues = transactions["input"]
                    # For each Test extract all the input requests
                    testData.append(extractInputTests(inputTestValues,userOverrides))
                elif 'output' in transactions.keys():
                    outputTestValues = transactions["output"]
                    testData.append(extractOutputTests(outputTestValues))
                elif 'meta' in transactions.keys():
                    # Check if we have enabled our test if not we'll skip
                    metaData = transactions["meta"]
                    if "enabled" in metaData.keys():
                        if metaData["enabled"] is False:
                            skipTest = True
                else:
                    return returnError("No input/output was found, please specify at least an empty input and out for defaults")
            # if the test is disabled we skip it
            if skipTest is True:
                continue
            # sanity check to ensure even number of in's and out's
            requests = 0
            responses = 0
            for i in testData:
                if i.__class__.__name__ == "TestRequest":
                    requests += 1
                if i.__class__.__name__ == "TestResponse":
                    responses += 1
            if requests != responses:
                return returnError("No input/output was found, please specify at least an empty input and out for defaults")
            #myTest = Test(testData, metaData)
            myTest = {
                'testData':     testData,
                'metaData':     metaData
            }
            myTests[section].append(myTest)
    return myTests

