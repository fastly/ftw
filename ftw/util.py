from __future__ import print_function

import glob
import yaml


def get_files(directory, extension):
    """
    Take a directory and an extension and return the files
    that match the extension
    """
    return glob.glob('%s/*.%s' % (directory, extension))


def extract_yaml(yaml_files):
    """
    Take a list of yaml_files and load them to return back
    to the testing program
    """
    loaded_yaml = []
    for yaml_file in yaml_files:
        try:
            with open(yaml_file, 'r') as fd:
                loaded_yaml.append(yaml.safe_load(fd))
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
