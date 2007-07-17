"""Crunchy: serving up interactive Python tutorials
At present Crunchy can only be started from here, as a script.
"""

import socket
import webbrowser
import sys
import imp

# import this so that py2exe knows to import modules that the plugins require
import all_plugins

# override the default find_module
# TODO: make this specific to win32 with py2exe
imp._find_module = imp.find_module

def _find_module(name, path=None):
    if name == "crunchy":
        return ("","","")
    return imp._find_module(name, path)

imp.find_module = _find_module

import src.configuration as configuration
import src.http_serve as http_serve
import src.cometIO as cometIO
import src.pluginloader as pluginloader

def find_port(start):
    """finds the first free port on 127.0.0.1 starting at start"""
    finalport = None
    testsock = socket.socket()
    testn = start
    while not finalport and (testn < 65536):
        try:
            testsock.bind(('127.0.0.1', testn))
            finalport = testn
        except socket.error:
            testn += 1
    testsock.close()
    return finalport

def run_crunchy():
    port = find_port(8002)
    print "Serving on port %s." % port
    server = http_serve.MyHTTPServer(('127.0.0.1', port), http_serve.HTTPRequestHandler)
    server.register_handler(cometIO.push_input, "/input")
    server.register_handler(cometIO.comet, "/comet")
    pluginloader.init_plugin_system(server)
    _url = 'http://127.0.0.1:' + str(port) + '/'
    webbrowser.open(_url)
    # print this info so that, if the right browser does not open,
    # the user can copy and paste the URL
    print '\nCrunchy Server: serving up interactive tutorials at URL %s\n'%_url
    server.still_serving = True
    while server.still_serving:
        server.handle_request()

if __name__ == "__main__":
    run_crunchy()
