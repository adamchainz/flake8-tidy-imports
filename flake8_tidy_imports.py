# -*- encoding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import ast

import flake8

__author__ = 'Adam Johnson'
__email__ = 'me@adamj.eu'
__version__ = '1.1.0'


class ImportChecker(object):
    """
    Flake8 plugin to make your import statements tidier.
    """
    name = 'flake8-tidy-imports'
    version = __version__

    def __init__(self, tree, *args, **kwargs):
        self.tree = tree

    @classmethod
    def add_options(cls, parser):
        kwargs = {
            'action': 'store',
            'default': '',
            'help': "A map of modules to ban to the error messages to "
                    "display in the error.",
        }
        if flake8.__version__.startswith('3.'):
            kwargs['parse_from_config'] = True

        parser.add_option('--banned-modules', **kwargs)

        if flake8.__version__.startswith('2.'):
            parser.config_options.append('banned-modules')

    @classmethod
    def parse_options(cls, options):
        lines = [line.strip() for line in options.banned_modules.split('\n')
                 if line.strip()]
        cls.banned_modules = {}
        for line in lines:
            if line.strip() == '{python2to3}':
                cls.banned_modules.update(cls.py3k_import_rules)
                continue
            if '=' not in line:
                raise ValueError("'=' not found")
            module, message = line.split('=', 1)
            module = module.strip()
            message = message.strip()
            cls.banned_modules[module] = message

    message_I200 = "I200 Unnecessary import alias - rewrite as '{}'."
    message_I201 = "I201 Banned import '{name}' used - {msg}."

    def run(self):
        for node in ast.walk(self.tree):

            for rule in ('I200', 'I201'):
                for err in getattr(self, 'rule_{}'.format(rule))(node):
                    yield err

    def rule_I200(self, node):
        if isinstance(node, ast.Import):
            for alias in node.names:

                if '.' not in alias.name:
                    from_name = None
                    imported_name = alias.name
                else:
                    from_name, imported_name = alias.name.rsplit('.', 1)

                if imported_name == alias.asname:

                    if from_name:
                        rewritten = 'from {} import {}'.format(
                            from_name, imported_name
                        )
                    else:
                        rewritten = 'import {}'.format(imported_name)

                    yield (
                        node.lineno,
                        node.col_offset,
                        self.message_I200.format(rewritten),
                        type(self)
                    )
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == alias.asname:

                    rewritten = 'from {} import {}'.format(node.module, alias.name)

                    yield (
                        node.lineno,
                        node.col_offset,
                        self.message_I200.format(rewritten),
                        type(self)
                    )

    def rule_I201(self, node):
        if isinstance(node, ast.Import):
            module_names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            node_module = node.module or ''
            module_names = [node_module]
            for alias in node.names:
                module_names.append('{}.{}'.format(node_module, alias.name))
        else:
            return

        # Sort from most to least specific paths.
        module_names.sort(key=len, reverse=True)

        warned = set()

        for module_name in module_names:

            if module_name in self.banned_modules:
                message = self.message_I201.format(
                    name=module_name,
                    msg=self.banned_modules[module_name]
                )
                if any(mod.startswith(module_name) for mod in warned):
                    # Do not show an error for this line if we already showed
                    # a more specific error.
                    continue
                else:
                    warned.add(module_name)
                yield (
                    node.lineno,
                    node.col_offset,
                    message,
                    type(self)
                )

    py3k_import_rules = {
        '__builtin__': 'moved in Python 3. six.moves.builtins can be used as a drop-in replacement',
        '_winreg': 'moved in Python 3. six.moves.winreg can be used as a drop-in replacement',
        'anydbm': 'moved in Python 3. dbm can be used as a drop-in replacement',
        'asynchat.fifo': 'removed in Python 3',
        'audiodev': 'removed in Python 3',
        'BaseHTTPServer': 'moved in Python 3. six.moves.BaseHTTPServer can be used as a drop-in replacement',
        'Bastion': 'removed in Python 3',
        'bsddb185': 'moved in Python 3. Use bsddb3 instead',
        'Canvas': 'removed in Python 3',
        'cfmfile': 'removed in Python 3',
        'CGIHTTPServer': 'moved in Python 3. six.moves.CGIHTTPServer can be used as a drop-in replacement',
        'cl': 'removed in Python 3',
        'commands': 'moved in Python 3. Use subprocess instead',
        'compiler': 'moved in Python 3. Use ast instead',
        'ConfigParser': 'moved in Python 3. six.moves.configparser can be used as a drop-in replacement',
        'contextlib.nested': 'moved in Python 3. Use Use the contextlib2.ExitStack backport or the shim in http://stackoverflow.com/a/39158985/303931 instead',  # noqa:E501
        'Cookie': 'moved in Python 3. six.moves.http_cookies can be used as a drop-in replacement',
        'cookielib': 'moved in Python 3. six.moves.http_cookiejar can be used as a drop-in replacement',
        'copy_reg': 'moved in Python 3. six.moves.copyreg can be used as a drop-in replacement',
        'cPickle': 'moved in Python 3. six.moves.cPickle can be used as a drop-in replacement',
        'cStringIO': 'moved in Python 3. io can be used as a drop-in replacement',
        'cStringIO.cStringIO': 'moved in Python 3. io.BytesIO can be used as a drop-in replacement',
        'cStringIO.StringIO': 'moved in Python 3. six.moves.cStringIO can be used as a drop-in replacement',
        'Dialog': 'moved in Python 3. six.moves.tkinter_dialog can be used as a drop-in replacement',
        'dircache': 'removed in Python 3',
        'dl': 'moved in Python 3. Use ctypes instead',
        'DocXMLRPCServer': 'moved in Python 3. Use six.moves.xmlrpc_server instead',
        'dummy_thread': 'moved in Python 3. six.moves._dummy_thread can be used as a drop-in replacement',
        'email.MIMEBase': 'moved in Python 3. six.moves.email_mime_base can be used as a drop-in replacement',
        'email.MIMEMultipart': 'moved in Python 3. six.moves.email_mime_multipart can be used as a drop-in replacement',  # noqa:E501
        'email.MIMENonMultipart': 'moved in Python 3. six.moves.email_mime_nonmultipart can be used as a drop-in replacement',  # noqa:E501
        'email.MIMEText': 'moved in Python 3. six.moves.email_mime_text can be used as a drop-in replacement',
        'FileDialog': 'moved in Python 3. six.moves.tkinter_filedialog can be used as a drop-in replacement',
        'fpformat': 'removed in Python 3',
        'ftplib.Netrc': 'removed in Python 3',
        'gdbm': 'moved in Python 3. six.moves.dbm_gnu can be used as a drop-in replacement',
        'htmlentitydefs': 'moved in Python 3. six.moves.html_entities can be used as a drop-in replacement',
        'htmllib': 'moved in Python 3. Use six.moves.html_parser instead',
        'HTMLParser': 'moved in Python 3. Other than HTMLParserError, six.moves.html_parser can be used as a drop-in replacement',  # noqa:E501
        'HTMLParser.HTMLParseError': 'Removed in Python 3.5+',
        'httplib': 'moved in Python 3. six.moves.http_client can be used as a drop-in replacement',
        'ihooks': 'removed in Python 3',
        'imageop': 'moved in Python 3. Use PIL/Pillow instead',
        'imputil': 'removed in Python 3',
        'inspect.getmoduleinfo': 'moved in Python 3. Use inspect.getmodulename instead',
        'itertools.ifilter': 'moved in Python 3. six.moves.filter can be used as a drop-in replacement',
        'itertools.ifilterfalse': 'moved in Python 3. six.moves.filterfalse can be used as a drop-in replacement',
        'itertools.imap': 'moved in Python 3. six.moves.map can be used as a drop-in replacement',
        'itertools.izip': 'moved in Python 3. six.moves.zip can be used as a drop-in replacement',
        'itertools.izip_longest': 'moved in Python 3. six.moves.zip_longest can be used as a drop-in replacement',
        'linuxaudiodev': 'moved in Python 3. Use ossaudiodev instead',
        'markupbase': 'moved in Python 3. Use _markupbase instead',
        'md5': 'moved in Python 3. hashlib can be used as a drop-in replacement',
        'md5.md5': 'moved in Python 3. hashlib.md5 can be used as a drop-in replacement',
        'md5.new': 'moved in Python 3. hashlib.md5 can be used as a drop-in replacement',
        'mhlib': 'moved in Python 3. Use mailbox instead',
        'mimetools': 'moved in Python 3. Use email instead',
        'MimeWriter': 'moved in Python 3. Use email instead',
        'mimify': 'moved in Python 3. Use email instead',
        'multifile': 'moved in Python 3. Use email instead',
        'mutex': 'removed in Python 3',
        'new': 'removed in Python 3',
        'os.getcwd': 'moved in Python 3. six.moves.getcwdb can be used as a drop-in replacement',
        'os.getcwdu': 'moved in Python 3. six.moves.getcwd can be used as a drop-in replacement',
        'pipes.quote': 'moved in Python 3. six.moves.shlex_quote can be used as a drop-in replacement',
        'platform._bcd2str': 'removed in Python 3',
        'platform._mac_ver_gstalt': 'removed in Python 3',
        'platform._mac_ver_lookup': 'removed in Python 3',
        'plistlib.readPlist': 'moved in Python 3. Use plistlib.load instead',
        'plistlib.readPlistFromBytes': 'moved in Python 3. Use plistlib.loads instead',
        'plistlib.writePlist': 'moved in Python 3. Use plistlib.dump instead',
        'plistlib.writePlistToBytes': 'moved in Python 3. Use plistlib.dumps instead',
        'popen2': 'moved in Python 3. Use subprocess instead',
        'posixfile': 'moved in Python 3. Use fcntl.lockf instead',
        'pure': 'removed in Python 3',
        'pydoc.Scanner': 'removed in Python 3',
        'Queue': 'moved in Python 3. six.moves.queue can be used as a drop-in replacement',
        'repr': 'moved in Python 3. six.moves.reprlib can be used as a drop-in replacement',
        'rexec': 'removed in Python 3',
        'rfc822': 'moved in Python 3. Use email instead',
        'robotparser': 'moved in Python 3. six.moves.urllib.robotparser can be used as a drop-in replacement',
        'ScrolledText': 'moved in Python 3. six.moves.tkinter_scrolledtext can be used as a drop-in replacement',
        'sgmllib': 'removed in Python 3',
        'sha': 'moved in Python 3. Use hashlib instead',
        'sha.new': 'moved in Python 3. hashlib.sha1 can be used as a drop-in replacement',
        'sha.sha': 'moved in Python 3. hashlib.sha1 can be used as a drop-in replacement',
        'SimpleDialog': 'moved in Python 3. six.moves.tkinter_simpledialog can be used as a drop-in replacement',
        'SimpleHTTPServer': 'moved in Python 3. six.moves.SimpleHTTPServer can be used as a drop-in replacement',
        'SimpleXMLRPCServer': 'moved in Python 3. six.moves.xmlrpc_server can be used as a drop-in replacement',
        'smtplib.SSLFakeFile': 'moved in Python 3. Use socket.socket.makefile instead',
        'SocketServer': 'moved in Python 3. six.moves.socketserver can be used as a drop-in replacement',
        'sre': 'moved in Python 3. Use re instead',
        'statvfs': 'moved in Python 3. Use os.statvfs instead',
        'string.atof': 'moved in Python 3. float can be used as a drop-in replacement',
        'string.atoi': 'moved in Python 3. int can be used as a drop-in replacement',
        'string.atol': 'moved in Python 3. int can be used as a drop-in replacement',
        'string.capitalize': 'removed in Python 3',
        'string.center': 'removed in Python 3',
        'string.count': 'removed in Python 3',
        'string.expandtabs': 'removed in Python 3',
        'string.find': 'removed in Python 3',
        'string.index': 'removed in Python 3',
        'string.join': 'removed in Python 3',
        'string.joinfields': 'removed in Python 3',
        'string.letters': 'moved in Python 3. string.ascii_letters can be used as a drop-in replacement',
        'string.ljust': 'removed in Python 3',
        'string.lower': 'removed in Python 3',
        'string.lowercase': 'moved in Python 3. string.ascii_lowercase can be used as a drop-in replacement',
        'string.lstrip': 'removed in Python 3',
        'string.maketrans': 'moved in Python 3. Use bytes.maketrans/bytearray.maketrans or a dict of unicode codepoints to substitutions instead',  # noqa:E501
        'string.replace': 'removed in Python 3',
        'string.rfind': 'removed in Python 3',
        'string.rindex': 'removed in Python 3',
        'string.rjust': 'removed in Python 3',
        'string.rsplit': 'removed in Python 3',
        'string.rstrip': 'removed in Python 3',
        'string.split': 'removed in Python 3',
        'string.splitfields': 'removed in Python 3',
        'string.strip': 'removed in Python 3',
        'string.swapcase': 'removed in Python 3',
        'string.translate': 'removed in Python 3',
        'string.upper': 'removed in Python 3',
        'string.uppercase': 'moved in Python 3. string.ascii_uppercase can be used as a drop-in replacement',
        'string.zfill': 'removed in Python 3',
        'StringIO': 'moved in Python 3. Use io.StringIO or io.BytesIO instead',
        'stringold': 'removed in Python 3',
        'sunaudio': 'removed in Python 3',
        'sv': 'removed in Python 3',
        'tarfile.S_IFBLK': 'moved in Python 3. stat.S_IFBLK can be used as a drop-in replacement',
        'tarfile.S_IFCHR': 'moved in Python 3. stat.S_IFCHR can be used as a drop-in replacement',
        'tarfile.S_IFDIR': 'moved in Python 3. stat.S_IFDIR can be used as a drop-in replacement',
        'tarfile.S_IFIFO': 'moved in Python 3. stat.S_IFIFO can be used as a drop-in replacement',
        'tarfile.S_IFLNK': 'moved in Python 3. stat.S_IFLNK can be used as a drop-in replacement',
        'tarfile.S_IFREG': 'moved in Python 3. stat.S_IFREG can be used as a drop-in replacement',
        'test.test_support': 'moved in Python 3. Use test.support instead',
        'test.testall': 'removed in Python 3',
        'thread': 'moved in Python 3. six.moves._thread can be used as a drop-in replacement',
        'time.accept2dyear': 'removed in Python 3',
        'timing': 'moved in Python 3. Use time.clock instead',
        'Tix': 'moved in Python 3. six.moves.tkinter_tix can be used as a drop-in replacement',
        'tkColorChooser': 'moved in Python 3. six.moves.tkinter_colorchooser can be used as a drop-in replacement',
        'tkCommonDialog': 'moved in Python 3. six.moves.tkinter_commondialog can be used as a drop-in replacement',
        'Tkconstants': 'moved in Python 3. six.moves.tkinter_constants can be used as a drop-in replacement',
        'Tkdnd': 'moved in Python 3. six.moves.tkinter_dnd can be used as a drop-in replacement',
        'tkFileDialog': 'moved in Python 3. six.moves.tkinter_tkfiledialog can be used as a drop-in replacement',
        'tkFont': 'moved in Python 3. six.moves.tkinter_font can be used as a drop-in replacement',
        'Tkinter': 'moved in Python 3. six.moves.tkinter can be used as a drop-in replacement',
        'tkMessageBox': 'moved in Python 3. six.moves.tkinter_messagebox can be used as a drop-in replacement',
        'tkSimpleDialog': 'moved in Python 3. six.moves.tkinter_tksimpledialog can be used as a drop-in replacement',
        'toaiff': 'removed in Python 3',
        'ttk': 'moved in Python 3. six.moves.tkinter_ttk can be used as a drop-in replacement',
        'types.BooleanType': 'moved in Python 3. bool can be used as a drop-in replacement',
        'types.BufferType': 'removed in Python 3',
        'types.ClassType': 'removed in Python 3',
        'types.ComplexType': 'moved in Python 3. complex can be used as a drop-in replacement',
        'types.DictionaryType': 'removed in Python 3',
        'types.DictProxyType': 'removed in Python 3',
        'types.DictType': 'moved in Python 3. dict can be used as a drop-in replacement',
        'types.EllipsisType': 'moved in Python 3. type(Ellipsis) can be used as a drop-in replacement',
        'types.FileType': 'removed in Python 3',
        'types.FloatType': 'moved in Python 3. float can be used as a drop-in replacement',
        'types.InstanceType': 'removed in Python 3',
        'types.IntType': 'moved in Python 3. six.integer_types can be used as a drop-in replacement',
        'types.ListType': 'moved in Python 3. list can be used as a drop-in replacement',
        'types.LongType': 'removed in Python 3',
        'types.NoneType': 'moved in Python 3. type(None) can be used as a drop-in replacement',
        'types.NotImplementedType': 'removed in Python 3',
        'types.ObjectType': 'removed in Python 3',
        'types.SliceType': 'removed in Python 3',
        'types.StringType': 'moved in Python 3. Use six.binary_types or six.text_types depdending on context instead',
        'types.StringTypes': 'moved in Python 3. six.string_types can be used as a drop-in replacement',
        'types.TupleType': 'moved in Python 3. tuple can be used as a drop-in replacement',
        'types.TypeType': 'moved in Python 3. six.class_types can be used as a drop-in replacement',
        'types.UnboundMethodType': 'removed in Python 3',
        'types.UnicodeType': 'moved in Python 3. six.text_type can be used as a drop-in replacement',
        'types.XRangeType': 'removed in Python 3',
        'urllib.ContentTooShortError': 'moved in Python 3. six.moves.urllib.error.ContentTooShortError can be used as a drop-in replacement',  # noqa:E501
        'urllib.FancyURLopener': 'moved in Python 3. six.moves.urllib.request.FancyURLopener can be used as a drop-in replacement',  # noqa:E501
        'urllib.getproxies': 'moved in Python 3. six.moves.urllib.request.getproxies can be used as a drop-in replacement',  # noqa:E501
        'urllib.pathname2url': 'moved in Python 3. six.moves.urllib.request.pathname2url can be used as a drop-in replacement',  # noqa:E501
        'urllib.proxy_bypass': 'moved in Python 3. six.moves.urllib.request.proxy_bypass can be used as a drop-in replacement',  # noqa:E501
        'urllib.quote': 'moved in Python 3. six.moves.urllib.parse.quote can be used as a drop-in replacement',
        'urllib.quote_plus': 'moved in Python 3. six.moves.urllib.parse.quote_plus can be used as a drop-in replacement',  # noqa:E501
        'urllib.splitquery': 'moved in Python 3. six.moves.urllib.parse.splitquery can be used as a drop-in replacement',  # noqa:E501
        'urllib.splittag': 'moved in Python 3. six.moves.urllib.parse.splittag can be used as a drop-in replacement',
        'urllib.splituser': 'moved in Python 3. six.moves.urllib.parse.splituser can be used as a drop-in replacement',  # noqa:E501
        'urllib.unquote': 'moved in Python 3. six.moves.urllib.parse.unquote can be used as a drop-in replacement',
        'urllib.unquote_plus': 'moved in Python 3. six.moves.urllib.parse.unquote_plus can be used as a drop-in replacement',  # noqa:E501
        'urllib.url2pathname': 'moved in Python 3. six.moves.urllib.request.url2pathname can be used as a drop-in replacement',  # noqa:E501
        'urllib.urlcleanup': 'moved in Python 3. six.moves.urllib.request.urlcleanup can be used as a drop-in replacement',  # noqa:E501
        'urllib.urlencode': 'moved in Python 3. six.moves.urllib.parse.urlencode can be used as a drop-in replacement',  # noqa:E501
        'urllib.URLopener': 'moved in Python 3. six.moves.urllib.request.URLopener can be used as a drop-in replacement',  # noqa:E501
        'urllib.urlretrieve': 'moved in Python 3. six.moves.urllib.request.urlretrieve can be used as a drop-in replacement',  # noqa:E501
        'urllib2': 'moved in Python 3. Use six.moves.urllib instead',
        'urllib2.AbstractBasicAuthHandler': 'moved in Python 3. six.moves.urllib.request.AbstractBasicAuthHandler can be used as a drop-in replacement',  # noqa:E501
        'urllib2.AbstractDigestAuthHandler': 'moved in Python 3. six.moves.urllib.request.AbstractDigestAuthHandler can be used as a drop-in replacement',  # noqa:E501
        'urllib2.BaseHandler': 'moved in Python 3. six.moves.urllib.request.BaseHandler can be used as a drop-in replacement',  # noqa:E501
        'urllib2.build_opener': 'moved in Python 3. six.moves.urllib.request.build_opener can be used as a drop-in replacement',  # noqa:E501
        'urllib2.CacheFTPHandler': 'moved in Python 3. six.moves.urllib.request.CacheFTPHandler can be used as a drop-in replacement',  # noqa:E501
        'urllib2.FileHandler': 'moved in Python 3. six.moves.urllib.request.FileHandler can be used as a drop-in replacement',  # noqa:E501
        'urllib2.FTPHandler': 'moved in Python 3. six.moves.urllib.request.FTPHandler can be used as a drop-in replacement',  # noqa:E501
        'urllib2.HTTPBasicAuthHandler': 'moved in Python 3. six.moves.urllib.request.HTTPBasicAuthHandler can be used as a drop-in replacement',  # noqa:E501
        'urllib2.HTTPCookieProcessor': 'moved in Python 3. six.moves.urllib.request.HTTPCookieProcessor can be used as a drop-in replacement',  # noqa:E501
        'urllib2.HTTPDefaultErrorHandler': 'moved in Python 3. six.moves.urllib.request.HTTPDefaultErrorHandler can be used as a drop-in replacement',  # noqa:E501
        'urllib2.HTTPDigestAuthHandler': 'moved in Python 3. six.moves.urllib.request.HTTPDigestAuthHandler can be used as a drop-in replacement',  # noqa:E501
        'urllib2.HTTPError': 'moved in Python 3. six.moves.urllib.error.HTTPError can be used as a drop-in replacement',  # noqa:E501
        'urllib2.HTTPErrorProcessor': 'moved in Python 3. six.moves.urllib.request.HTTPErrorProcessor can be used as a drop-in replacement',  # noqa:E501
        'urllib2.HTTPHandler': 'moved in Python 3. six.moves.urllib.request.HTTPHandler can be used as a drop-in replacement',  # noqa:E501
        'urllib2.HTTPPasswordMgr': 'moved in Python 3. six.moves.urllib.request.HTTPPasswordMgr can be used as a drop-in replacement',  # noqa:E501
        'urllib2.HTTPPasswordMgrWithDefaultRealm': 'moved in Python 3. six.moves.urllib.request.HTTPPasswordMgrWithDefaultRealm can be used as a drop-in replacement',  # noqa:E501
        'urllib2.HTTPRedirectHandler': 'moved in Python 3. six.moves.urllib.request.HTTPRedirectHandler can be used as a drop-in replacement',  # noqa:E501
        'urllib2.HTTPSHandler': 'moved in Python 3. six.moves.urllib.request.HTTPSHandler can be used as a drop-in replacement',  # noqa:E501
        'urllib2.install_opener': 'moved in Python 3. six.moves.urllib.request.install_opener can be used as a drop-in replacement',  # noqa:E501
        'urllib2.OpenerDirector': 'moved in Python 3. six.moves.urllib.request.OpenerDirector can be used as a drop-in replacement',  # noqa:E501
        'urllib2.ProxyBasicAuthHandler': 'moved in Python 3. six.moves.urllib.request.ProxyBasicAuthHandler can be used as a drop-in replacement',  # noqa:E501
        'urllib2.ProxyDigestAuthHandler': 'moved in Python 3. six.moves.urllib.request.ProxyDigestAuthHandler can be used as a drop-in replacement',  # noqa:E501
        'urllib2.ProxyHandler': 'moved in Python 3. six.moves.urllib.request.ProxyHandler can be used as a drop-in replacement',  # noqa:E501
        'urllib2.Request': 'moved in Python 3. six.moves.urllib.request.Request can be used as a drop-in replacement',
        'urllib2.UnknownHandler': 'moved in Python 3. six.moves.urllib.request.UnknownHandler can be used as a drop-in replacement',  # noqa:E501
        'urllib2.URLError': 'moved in Python 3. six.moves.urllib.error.URLError can be used as a drop-in replacement',
        'urllib2.urlopen': 'moved in Python 3. six.moves.urllib.request.urlopen can be used as a drop-in replacement',
        'urlparse': 'moved in Python 3. six.moves.urllib.parse can be used as a drop-in replacement',
        'urlparse.scheme_chars': 'moved in Python 3. Use urllib.parse.scheme_chars',
        'user': 'removed in Python 3',
        'UserDict': 'moved in Python 3. Use dict or collections.UserDict/collections.MutableMapping instead',
        'UserDict.UserDict': 'moved in Python 3. six.moves.UserDict can be used as a drop-in replacement',
        'UserDict.UserDictMixin': 'moved in Python 3. Use collections.MutableMapping instead',
        'UserList': 'moved in Python 3. Use list or collections.UserList/collections.MutableSequence instead',
        'UserList.UserList': 'moved in Python 3. six.moves.UserList can be used as a drop-in replacement',
        'UserString': 'moved in Python 3. Use six.text_type, six.binary_type or collections.UserString instead',
        'UserString.UserString': 'moved in Python 3. six.moves.UserString can be used as a drop-in replacement',
        'xmlrpclib': 'moved in Python 3. six.moves.xmlrpc_client can be used as a drop-in replacement',
    }
