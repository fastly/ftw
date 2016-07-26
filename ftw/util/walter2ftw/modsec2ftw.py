import os
import csv
import re
import yaml

import request_to_yaml

import sys


def walk_for_files(start_dir):
    our_files = []
    for root, dirs, files in os.walk(start_dir):
        for name in files:
            extension = os.path.splitext(name)[1]
            if extension == ".txt":
                our_files.append(os.path.join(root, name))
    return our_files

        

def process_file(filename):
    f = open(filename,'r')
    rule_id = "-1"
    rule_note = ""
    url = ""
    status = ""
    data = ""
    method = ""
    headers = ""
    for line in f.readlines():
        line = line.strip()
        if line[0] == "#":
            m = re.match(r'# Rule (\d+) \((.*)\)',line)
            if not m:
                print line
                m = re.match(r'# (.*) \(rule (\d+)\)',line)
                if not m:
                    continue
                    print line
                    sys.exit()
                rule_id = str(m.group(2))
                rule_note = m.group(1)
                continue
            rule_id = str(m.group(1))
            rule_note = m.group(2)
            continue
        else:
            comment = line.find('#')
            if comment != -1:
                # for the #
                rule_note = line[comment+1:].strip()
            else:
                walt_req = yaml.load(line)
                if(isinstance(walt_req,list)):
                    try:
                        walt_req = walt_req[0]["test"][0]
                    except:
                        continue
        try:
            url = walt_req["url"]
            status = walt_req["code"]
            data = walt_req["data"]
            method = walt_req["method"]
        except:
            pass
        metaDict = dict(
            author = "lifeforms",
            enabled = True,
            name = rule_id+".yaml",
            description = "None"
        )        
        inputDict = {}
        outputDict = {}
        inputDict["dest_addr"] = "127.0.0.1"      
        inputDict["port"] = 80      
        if method != "":
            inputDict["method"] = method
        if url != "":
            inputDict["uri"] = url
        if data != "":
            inputDict["data"] = data
        inputDict["headers"] = {"User-Agent":"ModSecurity CRS 3 Tests","Host":"localhost"}
        if(status == 200):
            outputDict["no_log_contains"] = "id \""+rule_id+"\""
        else:
            outputDict["log_contains"] = "id \""+rule_id+"\""
        data2 = dict(
            meta = metaDict,
            tests = [dict(
                atest_title = rule_id + "-1",
                desc = rule_note,
                stages = [dict(
                    stage = dict(
                        input = inputDict,
                        output = outputDict
                    )
                )]
            )]
        )
        yaml_out = yaml.dump(data2, default_flow_style=False)
        # Hacks for ordering in pyaml without going insane
        yaml_out = yaml_out.replace("atest_title:","\n  test_title:")
        yaml_out = yaml_out.replace("zdata:","data:")
        #yaml_out = yaml_out.replace("- test_title:","-\n  test_title:")
        #yaml_out = yaml_out.replace("- stage:","-\n    stage:")
        yaml_out = "---\n" + yaml_out 
        yaml_out = yaml_out.replace("\n","\n  ")
        
        out_f = "Output/" + rule_id+".yaml"
        out_f = out_f.replace("/",os.path.sep)      
        req = request_to_yaml.Request()
        req.write_yaml(out_f, yaml_out)
        

        print yaml_out


    
def main():
    files = walk_for_files('.')
    #for file in files:
    #    process_file(file)
    process_file(files[3])

main()