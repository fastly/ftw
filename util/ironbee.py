import os
import request_to_yaml

filelist = []
for root, dirs, files in os.walk("waf-research", topdown=False):
    for name in files:
        extension = name[-5:]
        if extension == ".test":
            filelist.append(os.path.join(root, name))
for fname in filelist:
    f = open(fname,'r')
    request = ""
    for line in f.readlines():
        if line[0] != '#':
            request += line
    req = request_to_yaml.Request()
    request = request.replace('\n','\r\n')
    req.get_request_line(request)
    req.get_headers(request)
    req.get_data(request)
    yaml_out = req.generate_yaml()
    newfname =  (fname.split('/')[-1]).split('.')[0]
    print newfname
    req.write_yaml('output/'+newfname+'.yaml',yaml_out)
    #print yaml_out

