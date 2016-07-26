import yaml
import os
import errno

class Request():
    def __init__(self):
        self.input = {}
        self.output = {}
        self.data_start = 0
        self.meta = {}
        self.test_title = ""
        self.desc = ""
    def double_quote(self,mystr):
        return mystr
        return "\"" + str(mystr) + "\""
    def generate_yaml(self):
        data = dict(
            meta = self.meta,
            tests = [dict(
                atest_title = self.test_title,
                desc = self.desc,
                stages = [dict(
                    stage = dict(
                        input = self.input,
                        output = self.output
                    )
                )]
            )]
        )
        
        yaml_out = yaml.dump(data, default_flow_style=False)
        # Hacks for ordering in pyaml without going insane
        yaml_out = yaml_out.replace("atest_title:","test_title:")
        yaml_out = yaml_out.replace("zdata:","data:")
        return yaml_out
        
    def get_request_line(self, req):
        req = req.split('\r\n')[0]
        req = req.split(' ',2)
        self.input["dest_addr"] = "127.0.0.1"      
        self.input["port"] = 80       
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
            # If we're still eating headers on the last iteration there is no body
            if num == len(req)-1:
                self.data_start = -1
            head = req[num].split(':')
            header[head[0]] = head[1].strip()
        self.input["headers"] = self.double_quote(header)

    def set_meta(self, author="None", name="None", description="None"):
        self.meta = dict(
            author = author,
            enabled = True,
            name = name,
            description = description
        )
        
    def set_output(self, output={"status":200}):       
        self.output = output
    
    def set_title(self, title="auto-generated test"):
        self.test_title=title

    def set_dsec(self, desc="auto-generated description"):
        self.desc=desc        
        
    def get_data(self, req):
        req = req.split('\r\n')[1:]
        multiline = []
        if self.data_start != -1:
            
            if len(req[self.data_start+1:]) > 1:
                for line in req[self.data_start+1:]:
                    multiline.append(line)
                data = multiline
            else:
               data = self.double_quote("\n".join(req[self.data_start+1:]))         
            self.input["zdata"] = data

    def write_yaml(self,fname, yaml_out):
        if not os.path.exists(os.path.dirname(fname)):
            try:
                os.makedirs(os.path.dirname(fname))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise          
        if os.path.exists(fname):
            f = open(fname,'a')
            f.write(yaml_out)
            print "\tAPPENDED"
        else:
            f = open(fname,'w')
            f.write(yaml_out)

# Example Usage
#req = Request()
#req.set_meta("csanders-git","TEST.yaml","None")
#req.set_title("title1")
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
