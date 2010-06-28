# lookup.py
# Copyright (C) 2006, 2007, 2008, 2009, 2010 Michael Bayer 
# mike_mp@zzzcomputing.com
#
# This module is part of Mako and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import os, stat, posixpath, re
from mako import exceptions, util
from mako.template import Template

try:
    import threading
except:
    import dummy_threading as threading
    
class TemplateCollection(object):
    def has_template(self, uri):
        try:
            self.get_template(uri)
            return True
        except exceptions.TemplateLookupException:
            return False

    def get_template(self, uri, relativeto=None):
        raise NotImplementedError()

    def filename_to_uri(self, uri, filename):
        """Convert the given filename to a uri relative to 
           this TemplateCollection."""
        
        return uri
        
    def adjust_uri(self, uri, filename):
        """Adjust the given uri based on the calling filename.
        
        When this method is called from the runtime, the 'filename' parameter
        is taken directly to the 'filename' attribute of the calling template.
        Therefore a custom TemplateCollection subclass can place any string
        identifier desired in the "filename" parameter of the Template objects
        it constructs and have them come back here.
        
        """
        return uri
        
class TemplateLookup(TemplateCollection):
    def __init__(self, 
                        directories=None, 
                        module_directory=None, 
                        filesystem_checks=True, 
                        collection_size=-1, 
                        format_exceptions=False, 
                        error_handler=None, 
                        disable_unicode=False, 
                        output_encoding=None, 
                        encoding_errors='strict', 
                        cache_type=None, 
                        cache_dir=None, cache_url=None,
                        cache_enabled=True, 
                        modulename_callable=None, 
                        default_filters=None, 
                        buffer_filters=(), 
                        imports=None, 
                        input_encoding=None, 
                        preprocessor=None):
                        
        self.directories = [posixpath.normpath(d) for d in
                            util.to_list(directories, ())
                            ]
        self.module_directory = module_directory
        self.modulename_callable = modulename_callable
        self.filesystem_checks = filesystem_checks
        self.collection_size = collection_size

        self.template_args = {
            'format_exceptions':format_exceptions, 
            'error_handler':error_handler, 
            'disable_unicode':disable_unicode, 
            'output_encoding':output_encoding, 
            'encoding_errors':encoding_errors, 
            'input_encoding':input_encoding, 
            'module_directory':module_directory, 
            'cache_type':cache_type, 
            'cache_dir':cache_dir or module_directory, 
            'cache_url':cache_url, 
            'cache_enabled':cache_enabled, 
            'default_filters':default_filters, 
            'buffer_filters':buffer_filters,  
            'imports':imports, 
            'preprocessor':preprocessor}

        if collection_size == -1:
            self._collection = {}
            self._uri_cache = {}
        else:
            self._collection = util.LRUCache(collection_size)
            self._uri_cache = util.LRUCache(collection_size)
        self._mutex = threading.Lock()
        
    def get_template(self, uri):
        try:
            if self.filesystem_checks:
                return self._check(uri, self._collection[uri])
            else:
                return self._collection[uri]
        except KeyError:
            u = re.sub(r'^\/+', '', uri)
            for dir in self.directories:
                srcfile = posixpath.normpath(posixpath.join(dir, u))
                if os.path.isfile(srcfile):
                    return self._load(srcfile, uri)
            else:
                raise exceptions.TopLevelLookupException(
                                    "Cant locate template for uri %r" % uri)

    def adjust_uri(self, uri, relativeto):
        """adjust the given uri based on the calling filename."""
        
        if uri[0] != '/':
            if relativeto is not None:
                return posixpath.join(posixpath.dirname(relativeto), uri)
            else:
                return '/' + uri
        else:
            return uri
            
    
    def filename_to_uri(self, filename):
        try:
            return self._uri_cache[filename]
        except KeyError:
            value = self._relativeize(filename)
            self._uri_cache[filename] = value
            return value
                    
    def _relativeize(self, filename):
        """Return the portion of a filename that is 'relative' 
           to the directories in this lookup.
           
        """
        
        filename = posixpath.normpath(filename)
        for dir in self.directories:
            if filename[0:len(dir)] == dir:
                return filename[len(dir):]
        else:
            return None
            
    def _load(self, filename, uri):
        self._mutex.acquire()
        try:
            try:
                # try returning from collection one 
                # more time in case concurrent thread already loaded
                return self._collection[uri]
            except KeyError:
                pass
            try:
                if self.modulename_callable is not None:
                    module_filename = self.modulename_callable(filename, uri)
                else:
                    module_filename = None
                self._collection[uri] = template = Template(
                                        uri=uri,
                                        filename=posixpath.normpath(filename),
                                        lookup=self, 
                                        module_filename=module_filename,
                                        **self.template_args)
                return template
            except:
                # if compilation fails etc, ensure 
                # template is removed from collection,
                # re-raise
                self._collection.pop(uri, None)
                raise
        finally:
            self._mutex.release()
            
    def _check(self, uri, template):
        if template.filename is None:
            return template
        if not os.path.exists(template.filename):
            self._collection.pop(uri, None)
            raise exceptions.TemplateLookupException(
                                "Cant locate template for uri %r" % uri)
        elif template.module._modified_time < \
                        os.stat(template.filename)[stat.ST_MTIME]:
            self._collection.pop(uri, None)
            return self._load(template.filename, uri)
        else:
            return template
            
    def put_string(self, uri, text):
        self._collection[uri] = Template(
                                    text, 
                                    lookup=self, 
                                    uri=uri, 
                                    **self.template_args)
        
    def put_template(self, uri, template):
        self._collection[uri] = template
            
