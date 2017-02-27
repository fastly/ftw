from __future__ import print_function

import yaml
import os
import sqlite3
import ruleset
from glob import glob

def get_insert_statement(table_name):
    """
    Prepare SQL statement to be inserted into the FTW journal
    """
    q = 'INSERT INTO {tn} (rule_id, test_id, time_start, time_end, response_blob, status_code, stage) VALUES(?, ?, ?, ?, ?, ?, ?)'.format(
        tn=table_name)
    return q
    

def instantiate_database(sqlite_file='ftwj.sqlite'):
    """
    Create journal database for FTW runs
    """
    table_name = 'ftw'
    col1 = 'rule_id'
    col1_t = 'INTEGER'
    col2 = 'test_id'
    col2_t = 'STRING'
    col3 = 'time_start'
    col3_t = 'TEXT'
    col4 = 'time_end'
    col4_t = 'TEXT'
    col5 = 'response_blob'
    col5_t = 'TEXT'
    col6 = 'status_code'
    col6_t = 'INTEGER'
    col7 = 'stage'
    col7_t = 'INTEGER'
    conn = sqlite3.connect(sqlite_file)
    cur = conn.cursor()

    q = 'CREATE TABLE {tn}({col1} {col1_t},{col2} {col2_t},{col3} {col3_t},{col4} {col4_t},{col5} {col5_t},{col6} {col6_t},{col7} {col7_t})'.format(
        tn=table_name,
        col1=col1, col1_t=col1_t,
        col2=col2, col2_t=col2_t,
        col3=col3, col3_t=col3_t,
        col4=col4, col4_t=col4_t,
        col5=col5, col5_t=col5_t,
        col6=col6, col6_t=col6_t,
        col7=col7, col7_t=col7_t)
    cur.execute(q)
    conn.commit()
    conn.close()

def get_rulesets(ruledir, recurse):
    """
    List of ruleset objects extracted from the yaml directory
    """
    if os.path.isdir(ruledir) and recurse:
        yaml_files = [y for x in os.walk(ruledir) for y in glob(os.path.join(x[0], '*.yaml'))]
    elif os.path.isdir(ruledir) and not recurse:
        yaml_files = get_files(ruledir, 'yaml')
    elif os.path.isfile(ruledir):
        yaml_files = [ruledir]
    extracted_files = extract_yaml(yaml_files)
    rulesets = []
    for extracted_yaml in extracted_files:
        rulesets.append(ruleset.Ruleset(extracted_yaml))
    return rulesets

def get_files(directory, extension):
    """
    Take a directory and an extension and return the files
    that match the extension
    """
    return glob('%s/*.%s' % (directory, extension))


def extract_yaml(yaml_files):
    """
    Take a list of yaml_files and load them to return back
    to the testing program
    """
    loaded_yaml = []
    for yaml_file in yaml_files:
        try:
            with open(yaml_file, 'r') as fd:
                loaded_yaml.append(yaml.load(fd))
        except IOError as e:
            print('Error reading file', yaml_file)
            raise e
        except yaml.YAMLError as e:
            print('Error parsing file', yaml_file)
            raise e
        except Exception as e:
            print('General error')
            raise e
    return loaded_yaml
