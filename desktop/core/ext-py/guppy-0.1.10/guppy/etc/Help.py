#._cv_part guppy.etc.Help
# -*- coding: utf-8 -*-

import cStringIO, inspect, os

THISDIR = os.path.dirname(__file__)
#print 'THISDIR',THISDIR


class GuppyDoc:
    def __init__(self, mod, str):
        #assert str is not None
        self.mod = mod
        if str is None:
            str = '???'
        
        str = self._substitute(str)

        self.str = str

    def __getitem__(self, idx):
        refs = {}
        refline = False
        for line in self.str.split('\n'):
            if line == 'References':
                refline = True
                continue
            elif not refline:
                continue
            line=line.strip()
            assert line.startswith('[')
            refstop=line.index(']')
            ref = line[1:refstop]
            refs[int(ref)] = line[refstop+1:].strip()
        url = refs[idx]
        url = self.mod.docurl(url)
        return self.mod.open_browser(url)


    def getheader(self):
        lines = self.str.split('\n')
        header = []
        for line in lines:
            if not line:
                break
            header.append(line)
        return '\n'.join(header)

    def _substitute(self, str):
        rp = self.mod._root.guppy.heapy.Use.reprefix
        str = str.replace('$HP.', rp)
        return str

    def __repr__(self):
        return self.str
        
    def __str__(self):
        return self.str
        
class Lister:
    def __init__(self):
        self.output = cStringIO.StringIO()

    def list(self, items, columns=4, width=80):
        items = items[:]
        colw = width / columns
        rows = (len(items) + columns - 1) / columns
        for row in range(rows):
            for col in range(columns):
                if 1:
                    i = col * rows + row
                else:
                    i = row * columns + col
                if i < len(items):
                    self.output.write(items[i])
                    if col < columns - 1:
                        self.output.write(' ' + ' ' * (colw-1 - len(items[i])))
            self.output.write('\n')
        return self

    def getvalue(self):
        return self.output.getvalue()


class GuppyDir(object):
    def __init__(self, li, obj, mod, opts='', **kwds):
        self.li = li
        self.obj = obj
        self.mod = mod
        self.opts = opts
        self.kwds = kwds
    def __call__(self, opts=None):
        li = self.li
        obj = self.obj
        mod = self.mod
        if opts is None:
            opts = self.opts
        return self.__class__(li, obj, mod, opts)

    def __getattr__(self, attr):
        return self.mod.getdoc2(self.obj, attr)

    def __getitem__(self, idx):
        return self.li[idx]

    def __repr__(self):
        opts = self.opts
        if 'L' in opts:
            r = ''
            for d in self.li:
                r += '*** ' + d + ' ***\n' + repr(getattr(self, d))+'\n\n'
        elif 'l' in opts:
            r = ''
            for d in self.li:
                t = getattr(self, d).getheader()
                if not (t.startswith(d) or t.startswith('x.'+d)):
                    t = d
                r += t + '\n\n'
        else:
            r = Lister().list(self.li).getvalue().rstrip()
        header = self.kwds.get('header','')
        if header: header += '\n'
        footer = self.kwds.get('footer','')
        if footer: footer = '\n'+footer
        r = header+r+footer
        return r

class _GLUECLAMP_:
    def dir(self, obj=None, opts='', **kwds):
        try:
            share = obj._share
        except AttributeError:
            return self.getdir_no_share(obj, opts, **kwds)
        clamp = share.Clamp
        dl = getattr(clamp, '_dir_',None)
        if dl is not None:
            dl = list(dl)
        else:
            dl = []
            private = getattr(clamp,'_private_',())
            try:
                imports = clamp._imports_
            except AttributeError:
                pass
            for imp in imports:
                ix = imp.find(':')
                if ix == -1: continue
                dl.append(imp[ix+1:])
            for gm in dir(clamp):
                if gm.startswith('_get_'):
                    dl.append(gm[5:])
                else:
                    if not gm.startswith('_'):
                        dl.append(gm)
            dl = [d for d in dl if not d in private]
        dl.sort()
        return GuppyDir(dl,obj,self, opts, **kwds)

    def getdir_no_share(self, obj, opts, **kwds):
        dl = dir(obj)
        dl = [d for d in dl if not d.startswith('_')]
        return GuppyDir(dl,obj,self, opts, **kwds)
        
    def getdoc2(self, obj, name):
        try:
            share = obj._share
        except AttributeError:
            return self.getdoc_no_share(obj, name)
        clamp = obj._share.Clamp
        try:
            imports = clamp._imports_
        except AttributeError:
            pass
        else:
            for imp in imports:
                ix = imp.find(':')
                if ix == -1: 
                    pass
                else:
                    if imp[ix+1:]==name:
                        return self.getdoc_import(obj, clamp, name, imp, ix)
        for gm in dir(clamp):
            if gm.startswith('_get_') and gm[5:]==name:
                return self.getdoc__get_(clamp, gm)
            else:
                if name==gm:
                    return self.getdoc_other(clamp, name)

        return GuppyDoc(self, '???')

    def getdoc_no_share(self, obj, name):
        try:
            doc = getattr(obj,'_doc_'+name)
        except AttributeError:
            pass
        else:
            return GuppyDoc(self, doc)

        cl = obj.__class__
        p = getattr(cl, name)
        if isinstance(p, property):
            docobj = p
        else:
            docobj = getattr(obj, name)

        return self.getdoc_obj(docobj)

    def getdoc__get_(self, clamp, gm):
        func = getattr(clamp, gm)
        doc = func.__doc__
        return GuppyDoc(self, doc)

    def getdoc_import(self, obj, clamp, name, imp, ix):
        doc = ''
        if hasattr(clamp, '_doc_'+name):
            doc = getattr(obj, '_doc_'+name)
        else:
            impobj = getattr(obj, imp[ix+1:])
            doc = getattr(impobj, '__doc__')
        return GuppyDoc(self, doc)

    def getdoc_obj(self, obj):
        doc = inspect.getdoc(obj)
        if doc is None:
            doc = '???'
        return GuppyDoc(self, doc)

    def getdoc_other(self, obj, name):
        attr = getattr(obj, name)
        doc = inspect.getdoc(attr)
        if doc:
            return GuppyDoc(self, doc)

        try:
            doc = getattr(obj, '_doc_'+name)
        except AttributeError:
            doc = ''
        if doc is None:
            doc = '?'
        print 'doc', doc
        return GuppyDoc(self, doc)


    def docurl(self, url):
        path = os.path.dirname(__file__)+'/../doc'
        url = 'file://'+path+'/'+url
        return url

    def open_browser(self, url):
        try:
            import webbrowser
            webbrowser.open(url)
        except ImportError: # pre-webbrowser.py compatibility
            if sys.platform == 'win32':
                os.system('start "%s"' % url)
            elif sys.platform == 'mac':
                try: import ic
                except ImportError: pass
                else: ic.launchurl(url)
            else:
                rc = os.system('netscape -remote "openURL(%s)" &' % url)
                if rc: os.system('netscape "%s" &' % url)

