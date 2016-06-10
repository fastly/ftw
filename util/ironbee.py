import os
import request_to_yaml

filelist = []
for root, dirs, files in os.walk("waf-research", topdown=False):
    for name in files:
        extension = name[-5:]
        if extension == ".test":
            filelist.append(os.path.join(root, name))
idcounter = 1000
tests = {}


for fname in filelist:
    testName = fname.split('/')[-2]
    if( testName not in tests.keys() ):
        tests[testName] = request_to_yaml.Request()
    # continously readd the title
    tests[testName].add_fname(testName+'.yaml')
    # incriment each test ID
    tests[testName].set_id(idcounter)
    idcounter += 1     
    f = open(fname,'r')
    request = ""
    for line in f.readlines():
        if line[0] != '#':
            request += line
        else:
            # ignore empty lines
            if line.strip() == "#":
                pass
            else:
                if line.find("# @") != -1:
                    pass
    request = request.replace('\n','\r\n')                    
    tests[testName].get_request_line(request)
    tests[testName].get_headers(request)
    tests[testName].get_data(request)    
    tests[testName].generate_test()

# Generate our test
for test in tests.keys():
    yaml_out = "test"
    tests[test].generate_header()
#    req.generate_test()
    yaml_out = tests[test].generate_yaml()    
    tests[test].write_yaml('output/'+test+'.yaml',yaml_out)
#    tests[test].write_yaml('output/'+test+'.yaml',yaml_out)

#    f = open(fname,'r')
#    request = ""
#    req = request_to_yaml.Request()
#    for line in f.readlines():
#        if line[0] != '#':
#            request += line
#        else:
#            # ignore empty lines
#            if line.strip() == "#":
#                pass
#            else:
#                if line.find("# @") != -1:
#                    pass
#                    #print line
#                else:
#                    req.add_description(line[2:].strip())
#    req.set_id(idcounter)
#    idcounter += 1                  
#    request = request.replace('\n','\r\n')
#    req.get_request_line(request)
#    req.get_headers(request)
#    req.get_data(request)
#    newfname =  (fname.split('/')[-1]).split('.')[0]
#    req.add_fname(newfname+'.yaml')
#    req.generate_header()
#    req.generate_test()
#    yaml_out = req.generate_yaml()
#    req.write_yaml('output/'+newfname+'.yaml',yaml_out)

