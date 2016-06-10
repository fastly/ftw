import yaml

class Request():
    def __init__(self):
        self.input = {}
        self.output = {}
        self.data_start = 0
        self.description = ""
        self.fname = ""
        self.id = -1
        self.data = {"meta":{},"tests":[]}
    def double_quote(self,mystr):
        return mystr
        return "\"" + str(mystr) + "\""
    def generate_header(self):
        self.data["meta"] = dict(
                author = "@csanders-git",
                enabled = True,
                name = self.fname,
                description = self.description 
            )
           
    def generate_yaml(self):
        #print self.data        
        return yaml.dump(self.data, default_flow_style=False)
    def generate_test(self):
        print   self.input

        self.data["tests"].append(dict(
            rule_id = self.id,
            stages = [dict(
                stage = dict(
                    input = self.input,
                    output = dict(
                        status = 200
                    )
                )
            )]
        ))
        self.input = {}
        #print self.data
    def add_description(self, description):
        self.description = description
    def add_fname(self, name):
        self.fname = name     
    def get_request_line(self, req):
        req = req.split('\r\n')[0]
        req = req.split(' ',2)
        self.input["method"] = self.double_quote(req[0])
        self.input["uri"] = self.double_quote(req[1])
        self.input["version"] = self.double_quote(req[2])
        
    def get_headers(self, req):
        req = req.split('\r\n')[1:]
        header = {}
        for num in range(len(req)):
            if req[num] == '':
                self.data_start = num
                break
            head = req[num].split(':')
            header[head[0]] = head[1].strip()
        self.input["headers"] = self.double_quote(header)
    def get_data(self, req):
        req = req.split('\r\n')[1:]
        self.input["data"] = self.double_quote("\r\n".join(req[self.data_start+1:]))
    def set_id(self, id):
        self.id = id
    def write_yaml(self,fname, yaml_out):
        f = open(fname,'w')
        f.write(yaml_out)

# Example Usage
#req = Request()
#
#request = """GET / HTTP/1.1
#User-Agent: test:/data
#
#xyz
#
#"""
#request = request.replace('\n','\r\n')
#req.get_request_line(request)
#req.get_headers(request)
#req.get_data(request)
#yaml_out = req.generate_yaml()
#write_yaml('out.yaml', yaml_out)
