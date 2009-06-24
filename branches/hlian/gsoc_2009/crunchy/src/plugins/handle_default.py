"""This plugin handles loading all pages not loaded by other plugins"""

import os
import sys
from os.path import normpath, join, isdir, exists

# All plugins should import the crunchy plugin API via interface.py
from src.interface import translate, plugin, server, debug, \
                      debug_msg, preprocessor

_ = translate['_']

def register():
    '''registers a default http handler'''
    plugin['register_http_handler'](None, handler)

# the root of the server is in a separate directory:
root_path = join(plugin['get_root_dir'](), "server_root/")

def path_to_filedata(path, root, crunchy_username=None):
    """ Given a path, finds the matching file and returns a read-only
    reference to it. If the path specifies a directory and does not
    have a trailing slash (ie. /example instead of /example/) this
    function will return none, the browser should then be redirected
    to the same path with a trailing /. Root is the fully qualified
    path to server root. Paths starting with / and containing .. will
    return an error message. POSIX version, should work in Windows.
    Data will be returned in encoded, non-Unicode form because the
    path could point to a binary file and is tailored for the
    request.wfile.write method.
    """
    if path == server['exit']:
        server['server'].still_serving = False
        exit_file = join(root_path, "exit_en.html")
        return open(exit_file).read()
    if path.startswith("/") and (path.find("/../") != -1):
        return error_page(path).encode('utf8')
    if exists(path) and path != "/":
        npath = path
    else:
        npath = normpath(join(root, normpath(path[1:])))

    if isdir(npath):
        if path[-1] != "/":
            return None
        else:
            return get_directory(npath, crunchy_username).encode('utf8')
    else:
        try:
            extension = npath.split('.')[-1]
            if extension in ["htm", "html"]:
                text = plugin['create_vlam_page']
                text = text(open(npath), path, crunchy_username)
                text = text.read().encode('utf8')
                return text
            elif extension in preprocessor:
                text = plugin['create_vlam_page']
                text = text(preprocessor[extension](npath), path, crunchy_username)
                text = text.read().encode('utf8')
                return text
            # we need binary mode because otherwise the file may not get
            # read properly on windows (e.g. for image files)
            return open(npath, mode="rb").read()
        except IOError:
            try:
                return open(npath.encode(sys.getfilesystemencoding()),
                            mode="rb").read()
            except IOError:
                print("In path_to_filedata, can not open path = " + npath)
                return error_page(path)

tell_Safari_page_is_html = False

def handler(request):
    """the actual handler"""
    global tell_Safari_page_is_html
    if debug['handle_default'] or debug['handle_default.handler']:
        debug_msg("--> entering handler() in handle_default.py")
    try:
        username = request.crunchy_username
    except:
        request.wfile.write(_("You need to create an account before you can use Crunchy. "))
        request.wfile.write(_("Please use account_manager.py to create an account."))
        exit_file = join(root_path, "exit_en.html")
        request.wfile.write(open(exit_file).read())
        request.end_headers()
        server['server'].still_serving = False
        return

    data = path_to_filedata(request.path, root_path, request.crunchy_username)
    if debug['handle_default'] or debug['handle_default.handler']:
        debug_msg("in handle_default.handler(), beginning of data =")
        try:
            d = data[0:80]
            if "\n" in d:
                d = d.split("\n")[0]
            debug_msg(d)
        except:
            debug_msg(data)
    if data == None:
        request.send_response(301)
        request.send_header("Location", request.path + "/")
        request.end_headers()
    else:
        request.send_response(200)
        # Tell Firefox not to cache; otherwise back button can bring back to
        # a page with a broken interpreter
        request.send_header('Cache-Control', 'no-cache, must-revalidate, no-store')
        if tell_Safari_page_is_html:
            request.send_header ("Content-Type", "text/html; charset=UTF-8")
            tell_Safari_page_is_html = False
        request.end_headers()
        try:
            request.wfile.write(data)
        except:  # was introduced to deal with Python 3.x problems
            print("Error in handle_default; should not have happened!")
            raise

def list_directory(path):
    '''Returns a list of files and annotated directories in a path.'''
    childs = os.listdir(path)
    def annotate(child):
        if isdir(os.path.join(path, child)):
            return child + '/'
        else:
            return child
    return map(annotate, childs)

def get_directory(npath, crunchy_username):
    '''Returns a directory listing from a path. If index.htm or
    index.html exists, it returns that page instead.'''
    global tell_Safari_page_is_html

    childs = list_directory(npath)
    for i in ["index.htm", "index.html"]:
        if i in childs:
            tell_Safari_page_is_html = True
            return path_to_filedata("/"+i, npath, crunchy_username)

    def to_bullet(x):
        return '<li><a href="%s">%s</a></li>' % (x, x)

    tstring = u''.join(to_bullet(child) for child in childs)
    return dir_list_page % (_("Directory Listing"), tstring)

not_found = open(join(root_path, "404.html")).read()

dir_list_page = u"""
<html>
<head>
<title>
%s
</title>
</head>
<body>
<ul>
<li><a href="../">..</a></li>
%s
</ul>
</body>
</html>
"""

def error_page(path):
    '''returns a page with an error message; used when a path is not found'''
    return not_found % (path, path)