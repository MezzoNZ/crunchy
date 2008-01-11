'''
mocks.py

This file contains mock objects used for testing.  Since so many plugins
rely on the same page structure, etc., having a set of mock objects that
can be reused can save a fair bit of time and ensure a greater consistency
in the various tests.
'''
import sys
from src.interface import plugin, python_version, python_minor_version

registered_tag_handler = {}
registered_http_handler = {}
registered_services = {}

class Page(object):
    '''Fake page used for testing.
    A page can be modified by a plugin when some information is added to it.
    This class keeps track of the type of information that was added - but
    not the details.
    
    Note that verification of modifications of Elements are done separately.'''
    def __init__(self):
        self.pageid = 1
        self.added_info = []
        self.url = ''
    
    def includes(self, dummy):
        self.added_info.append('includes')
    
    def add_include(self, function):
        self.added_info.append(('add_include', function))
    
    def add_js_code(self, dummy):
        self.added_info.append('add_js_code')
    
    def insert_js_file(self, filename):
        self.added_info.append(('insert_js_file', filename))
        
    def add_css_file(self, filename):
        self.added_info.append(('add_css_file', filename))

    def add_css_code(self, dummy):
        self.added_info.append('add_css_code')


class Wfile(object):
    '''fake Wfile added as attribute of Request object.'''
    def write(self, text):
        # required to make this work when the file is read in binary mode
        if python_version >= 3 and python_minor_version == 'a2':
            if isinstance(text, bytes):
                str_text = str(text.decode(sys.getfilesystemencoding()))
                print(str_text)
            else:
                print(text)
        else:
            print(text)
        

class Request(object):
    '''Totally fake request object'''
    def __init__(self, data='data', args='args'):
        self.data = data
        self.args = args
        self.wfile = Wfile()
        
    def send_response(self, response=42):
        print(response)
        
    def end_headers(self):
        print("End headers")


def register_tag_handler(tag, attribute, value, function):
    if tag not in registered_tag_handler:
        registered_tag_handler[tag] = {}
    if attribute not in registered_tag_handler[tag]:
        registered_tag_handler[tag][attribute] = {}
    registered_tag_handler[tag][attribute][value] = function
plugin['register_tag_handler'] = register_tag_handler

def register_http_handler(handle, function):
    registered_http_handler[handle] = function
plugin['register_http_handler'] = register_http_handler

def register_service(handle, function):
    registered_services[handle] = function
plugin['register_service'] = register_service

