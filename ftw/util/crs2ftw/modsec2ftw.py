import os
import csv
import re
import yaml

import request_to_yaml

import sys

renumbering_list = []

def walk_for_files(start_dir):
    our_files = []
    for root, dirs, files in os.walk(start_dir):
        for name in files:
            extension = os.path.splitext(name)[1]
            if extension == ".tests":
                our_files.append(os.path.join(root, name))
    return our_files

def load_renumbering(location):
    renumbering_name = "IdNumbering.csv"
    full_name = location + renumbering_name
    with open(full_name, 'rb') as f:
        reader = csv.reader(f)
        global renumbering_list
        renumbering_list = map(tuple,reader)

def check_list(old_id):
    global renumbering_list
    for entry in renumbering_list:
        if entry[0] == old_id:
            return entry[1]
    return -1
        

def process_file(filename):
    f = open(filename,'r')
    out_test = {}
    rule_id = ""
    title = ""
    method = ""
    output = ""
    tests = f.read().split("%test ")
    for test in tests[1:]:
        #print test
        test_split = test.split('\n')
        name = test_split[0]
        print name
        # Get the ID of the rule
        try:
            rule = test.split('%output')[1]
            rule = rule.split('\n')[0]
            rule_id = rule.strip()
        except:
            # Hunt in the title
            m = re.match(r'.*\((\d+)\).*', name)
            if m:
                rule_id = m.group(1)
            else:
                print "FAILURE"
                sys.exit()    
        # Go hutin for vars
        vars = {}
        vars_found = test.split('%var ')[1:]
        # We found some vars add them to our list
        if len(vars_found) != 0:
            # Remove trailing newlines
            for i in range(0,len(vars_found)):
                vars_found[i] = vars_found[i].strip()
            # Remove the rest of the request from after the last var
            vars_found[-1] =  vars_found[-1].split('\n')[0]
            # Add them to our list of vars
            for var in vars_found:
                our_var = var.split('=')
                try:
                    vars[our_var[0]].append(our_var[1])
                except KeyError:
                    vars[our_var[0]] = [our_var[1]]
        if check_list(rule_id) != -1:
            new_id = check_list(rule_id)
            req = request_to_yaml.Request()
            req.set_meta("csanders-git",new_id+".yaml","None")
            req.set_title(new_id + "-1")
            name = name.replace(rule_id,check_list(rule_id))
            req.set_dsec(name + " from old modsec regressions")
            req.set_output({"log_contains": "id \""+new_id+"\""})
            # Get the request
            request = test.split('%request\n')[1]
            # Remove extra new line at end
            request = request.split("\n\n\n")[0]
            request = request.replace('\n','\r\n')
            # we replace the host with localhost always
            request = request.replace("$hostname", "localhost")
            # We'll auto handle content length
            request = request.replace("\nContent-Length: $CONTENT_LENGTH","")
            # Generate output name
            out_f = "Output/" + filename + "/" + new_id+".yaml"
            out_f = out_f.replace("/",os.path.sep)
            out_f = out_f.replace(".tests","")            
            # This crazy var thing needs to happen
            # No idea what happens if there are two vars
            if len(vars) > 0:
                for varname in vars.keys():
                    for varvalue in vars[varname]:
                        new_request = request.replace("$" + varname, varvalue)
                        # Replace variables
                        req.get_request_line(new_request)
                        req.get_headers(new_request)
                        req.get_data(new_request)
                        yaml_out = req.generate_yaml()
                        path = "Output/"+new_id+".yaml"
                        req.write_yaml(out_f, yaml_out)
                        print "wrote to file"
            else:                      
                # Replace variables
                req.get_request_line(request)
                req.get_headers(request)
                req.get_data(request)
                yaml_out = req.generate_yaml()
                req.write_yaml(out_f, yaml_out)
                print "wrote to file"            
        else:
            print "No longer supported"



    
def main():
    load_renumbering('../../../id_renumbering/')
    #print check_list('959073')
    files = walk_for_files('.')
    for file in files:
        process_file(file)

main()