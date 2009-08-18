# -*- coding: utf-8 -*-
"""handle local loading of tutorials (not from the server root).
Uses the /local http request path.

Also creates a form allowing to browse for a local tutorial to be loaded
by Crunchy.
"""
import os
import sys

# All plugins should import the crunchy plugin API via interface.py
from src.interface import config, plugin, python_version, translate
_ = translate['_']

if python_version < 3:
    from urllib import unquote_plus
else:
    from urllib.parse import unquote_plus

provides = set(["/local"])
requires = set(["filtered_dir", "insert_file_tree"])

LOCAL_HTML = "local_html"

def register():  # tested
    '''registers the plugins so that Crunchy can use them'''
    plugin['register_http_handler']("/local", local_loader)
    plugin['register_tag_handler']("meta", "title", "python_import", add_to_path)
    plugin['register_tag_handler']("div", "title", "local_html_file",
                                                 insert_load_local)
    plugin['add_vlam_option']('power_browser', LOCAL_HTML)
    plugin['register_http_handler']("/jquery_file_tree_html", jquery_file_tree_html)
    plugin['register_service'](LOCAL_HTML, insert_load_local)

def local_loader(request):  # tested
    '''loads a local file;
    if it determines that it is an html file (based on the extension), it
    creates a new vlam page from it and, if not already present, adds the
    base path to sys.path - so that any python file located in the same
    directory could be imported.

    If it is not an html file, it simply reads the file.'''
    url = unquote_plus(request.args["url"])
    extension = url.split('.')[-1]
    username = request.crunchy_username
    if "htm" in extension:
        page = plugin['create_vlam_page'](open(url), url, username=username,
                                          local=True)
        # The following will make it possible to include python modules
        # with tutorials so that they can be imported.
        base_url, dummy = os.path.split(url)
        if base_url not in sys.path:
            sys.path.insert(0, base_url)
    else:
        page = open(url, 'r')
    request.send_response(200)
    request.send_header('Cache-Control', 'no-cache, must-revalidate, no-store')
    request.end_headers()
    # write() in python 3.0 returns an int instead of None;
    # this interferes with unit tests
    # also, in Python 3, need to convert between bytes and strings...
    __irrelevant = request.wfile.write(page.read().encode('utf-8'))

def add_to_path(page, elem, *dummy):  # tested
    '''adds a path, relative to the html tutorial, to the Python path'''
    base_url, dummy = os.path.split(page.url)
    try:
        import_path = elem.attrib['name']
    except:
        return
    if page.is_from_root:
        added_path = os.path.normpath(os.path.join(
                                        config['crunchy_base_dir'],
                                    "server_root", base_url[1:], import_path))
    else:
        added_path = os.path.normpath(os.path.join(base_url, import_path))
    if added_path not in sys.path:
        sys.path.insert(0, added_path)

def insert_load_local(page, elem, uid):
    "Inserts a javascript browser object to load a local (html) file."
    plugin['services'].insert_file_tree(page, elem, uid, '/jquery_file_tree_html',
                                '/local', _('Load local html tutorial'),
                                _('Load tutorial'))
    return
plugin[LOCAL_HTML] = insert_load_local

def filter_html(filename, basepath):
    '''filters out all files and directory with filename so as to include
       only files whose extensions start with ".htm" with the possible
       exception of ".crunchy" - the usual crunchy default directory.
    '''
    if filename.startswith('.') and filename != ".crunchy":
        return True
    else:
        fullpath = os.path.join(basepath, filename)
        if os.path.isdir(fullpath):
            return False   # do not filter out directories
        ext = os.path.splitext(filename)[1][1:] # get .ext and remove dot
        if ext.startswith("htm"):
            return False
        else:
            return True

def jquery_file_tree_html(request):
    '''extract the file information and formats it in the form expected
       by the jquery FileTree plugin, but excludes some normally hidden
       files or directories, to include only html files.'''
    plugin['services'].filtered_dir(request, filter_html)
    return
