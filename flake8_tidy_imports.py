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
            if '=' not in line:
                raise ValueError("'=' not found")
            module, message = line.split('=', 1)
            module = module.strip()
            message = message.strip()
            cls.banned_modules[module] = message

    message_I200 = "I200 Unnecessary import alias - rewrite as '{}'."
    message_I201 = "I201 Banned import '{name}' used - {msg}."
    message_I203 = "I203 {msg}"

    def run(self):
        for node in ast.walk(self.tree):

            for rule in ('I200', 'I201', 'I203'):
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

    def rule_I203(self, node):
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

            if module_name in self.py3k_import_rules:
                message = self.message_I203.format(
                    name=module_name,
                    msg=self.py3k_import_rules[module_name]
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
        '__builtin__': '__builtin__ is moved in Python3. six.moves.builtins can be used as a drop-in replacement.',
        '_winreg': '_winreg is moved in Python3. six.moves.winreg can be used as a drop-in replacement.',
        'anydbm': 'anydbm is moved in Python3. dbm can be used as a drop-in replacement.',
        'asynchat.fifo': 'asynchat.fifo is removed in Python 3.',
        'audiodev': 'audiodev is removed in Python 3.',
        'BaseHTTPServer': 'BaseHTTPServer is moved in Python3. six.moves.BaseHTTPServer can be used as a drop-in replacement.',  # noqa:E501
        'Bastion': 'Bastion is removed in Python 3.',
        'bsddb185': 'bsddb185 is moved in Python 3. Use bsddb3 instead',
        'Canvas': 'Canvas is removed in Python 3.',
        'cfmfile': 'cfmfile is removed in Python 3.',
        'CGIHTTPServer': 'CGIHTTPServer is moved in Python3. six.moves.CGIHTTPServer can be used as a drop-in replacement.',  # noqa:E501
        'cl': 'cl is removed in Python 3.',
        'commands': 'commands is moved in Python 3. Use subprocess instead',
        'compiler': 'compiler is moved in Python 3. Use ast instead',
        'ConfigParser': 'ConfigParser is moved in Python3. six.moves.configparser can be used as a drop-in replacement.',  # noqa:E501
        'contextlib.nested': 'contextlib.nested is moved in Python 3. Use Use the contextlib2.ExitStack backport or the shim in http://stackoverflow.com/a/39158985/303931 instead',  # noqa:E501
        'Cookie': 'Cookie is moved in Python3. six.moves.http_cookies can be used as a drop-in replacement.',
        'cookielib': 'cookielib is moved in Python3. six.moves.http_cookiejar can be used as a drop-in replacement.',
        'copy_reg': 'copy_reg is moved in Python3. six.moves.copyreg can be used as a drop-in replacement.',
        'cPickle': 'cPickle is moved in Python3. six.moves.cPickle can be used as a drop-in replacement.',
        'cProfile': 'cProfile is moved in Python 3. Use _profile (C) or profile (Python) instead',
        'cStringIO': 'cStringIO is moved in Python3. io can be used as a drop-in replacement.',
        'cStringIO.cStringIO': 'cStringIO.cStringIO is moved in Python3. io.BytesIO can be used as a drop-in replacement.',  # noqa:E501
        'cStringIO.StringIO': 'cStringIO.StringIO is moved in Python3. six.moves.cStringIO can be used as a drop-in replacement.',  # noqa:E501
        'Dialog': 'Dialog is moved in Python3. six.moves.tkinter_dialog can be used as a drop-in replacement.',
        'dircache': 'dircache is removed in Python 3.',
        'dl': 'dl is moved in Python 3. Use ctypes instead',
        'DocXMLRPCServer': 'DocXMLRPCServer is moved in Python 3. Use six.moves.xmlrpc_server instead',
        'dummy_thread': 'dummy_thread is moved in Python3. six.moves._dummy_thread can be used as a drop-in replacement.',  # noqa:E501
        'email.MIMEBase': 'email.MIMEBase is moved in Python3. six.moves.email_mime_base can be used as a drop-in replacement.',  # noqa:E501
        'email.MIMEMultipart': 'email.MIMEMultipart is moved in Python3. six.moves.email_mime_multipart can be used as a drop-in replacement.',  # noqa:E501
        'email.MIMENonMultipart': 'email.MIMENonMultipart is moved in Python3. six.moves.email_mime_nonmultipart can be used as a drop-in replacement.',  # noqa:E501
        'email.MIMEText': 'email.MIMEText is moved in Python3. six.moves.email_mime_text can be used as a drop-in replacement.',  # noqa:E501
        'FileDialog': 'FileDialog is moved in Python3. six.moves.tkinter_filedialog can be used as a drop-in replacement.',  # noqa:E501
        'fpformat': 'fpformat is removed in Python 3.',
        'ftplib.Netrc': 'ftplib.Netrc is removed in Python 3.',
        'gdbm': 'gdbm is moved in Python3. six.moves.dbm_gnu can be used as a drop-in replacement.',
        'htmlentitydefs': 'htmlentitydefs is moved in Python3. six.moves.html_entities can be used as a drop-in replacement.',  # noqa:E501
        'htmllib': 'htmllib is moved in Python 3. Use six.moves.html_parser instead',
        'HTMLParser': 'HTMLParser is moved in Python3. six.moves.html_parser can be used as a drop-in replacement.',
        'httplib': 'httplib is moved in Python3. six.moves.http_client can be used as a drop-in replacement.',
        'ihooks': 'ihooks is removed in Python 3.',
        'imageop': 'imageop is moved in Python 3. Use PIL/Pillow instead',
        'imputil': 'imputil is removed in Python 3.',
        'inspect.getmoduleinfo': 'inspect.getmoduleinfo is moved in Python 3. Use inspect.getmodulename instead',
        'itertools.ifilter': 'itertools.ifilter is moved in Python3. six.moves.filter can be used as a drop-in replacement.',  # noqa:E501
        'itertools.ifilterfalse': 'itertools.ifilterfalse is moved in Python3. six.moves.filterfalse can be used as a drop-in replacement.',  # noqa:E501
        'itertools.imap': 'itertools.imap is moved in Python3. six.moves.map can be used as a drop-in replacement.',
        'itertools.izip': 'itertools.izip is moved in Python3. six.moves.zip can be used as a drop-in replacement.',
        'itertools.izip_longest': 'itertools.izip_longest is moved in Python3. six.moves.zip_longest can be used as a drop-in replacement.',  # noqa:E501
        'linuxaudiodev': 'linuxaudiodev is moved in Python 3. Use ossaudiodev instead',
        'markupbase': 'markupbase is moved in Python 3. Use _markupbase instead',
        'md5': 'md5 is moved in Python3. hashlib can be used as a drop-in replacement.',
        'md5.md5': 'md5.md5 is moved in Python3. hashlib.md5 can be used as a drop-in replacement.',
        'md5.new': 'md5.new is moved in Python3. hashlib.md5 can be used as a drop-in replacement.',
        'mhlib': 'mhlib is moved in Python 3. Use mailbox instead',
        'mimetools': 'mimetools is moved in Python 3. Use email instead',
        'MimeWriter': 'MimeWriter is moved in Python 3. Use email instead',
        'mimify': 'mimify is moved in Python 3. Use email instead',
        'multifile': 'multifile is moved in Python 3. Use email instead',
        'mutex': 'mutex is removed in Python 3.',
        'new': 'new is removed in Python 3.',
        'os.getcwd': 'os.getcwd is moved in Python3. six.moves.getcwdb can be used as a drop-in replacement.',
        'os.getcwdu': 'os.getcwdu is moved in Python3. six.moves.getcwd can be used as a drop-in replacement.',
        'pipes.quote': 'pipes.quote is moved in Python3. six.moves.shlex_quote can be used as a drop-in replacement.',
        'platform._bcd2str': 'platform._bcd2str is removed in Python 3.',
        'platform._mac_ver_gstalt': 'platform._mac_ver_gstalt is removed in Python 3.',
        'platform._mac_ver_lookup': 'platform._mac_ver_lookup is removed in Python 3.',
        'plistlib.readPlist': 'plistlib.readPlist is moved in Python 3. Use plistlib.load instead',
        'plistlib.readPlistFromBytes': 'plistlib.readPlistFromBytes is moved in Python 3. Use plistlib.loads instead',
        'plistlib.writePlist': 'plistlib.writePlist is moved in Python 3. Use plistlib.dump instead',
        'plistlib.writePlistToBytes': 'plistlib.writePlistToBytes is moved in Python 3. Use plistlib.dumps instead',
        'popen2': 'popen2 is moved in Python 3. Use subprocess instead',
        'posixfile': 'posixfile is moved in Python 3. Use fcntl.lockf instead',
        'pure': 'pure is removed in Python 3.',
        'pydoc.Scanner': 'pydoc.Scanner is removed in Python 3.',
        'Queue': 'Queue is moved in Python3. six.moves.queue can be used as a drop-in replacement.',
        'repr': 'repr is moved in Python3. six.moves.reprlib can be used as a drop-in replacement.',
        'rexec': 'rexec is removed in Python 3.',
        'rfc822': 'rfc822 is moved in Python 3. Use email instead',
        'robotparser': 'robotparser is moved in Python3. six.moves.urllib.robotparser can be used as a drop-in replacement.',  # noqa:E501
        'ScrolledText': 'ScrolledText is moved in Python3. six.moves.tkinter_scrolledtext can be used as a drop-in replacement.',  # noqa:E501
        'sgmllib': 'sgmllib is removed in Python 3.',
        'sha': 'sha is moved in Python 3. Use hashlib instead',
        'sha.new': 'sha.new is moved in Python3. hashlib.sha1 can be used as a drop-in replacement.',
        'sha.sha': 'sha.sha is moved in Python3. hashlib.sha1 can be used as a drop-in replacement.',
        'SimpleDialog': 'SimpleDialog is moved in Python3. six.moves.tkinter_simpledialog can be used as a drop-in replacement.',  # noqa:E501
        'SimpleHTTPServer': 'SimpleHTTPServer is moved in Python3. six.moves.SimpleHTTPServer can be used as a drop-in replacement.',  # noqa:E501
        'SimpleXMLRPCServer': 'SimpleXMLRPCServer is moved in Python3. six.moves.xmlrpc_server can be used as a drop-in replacement.',  # noqa:E501
        'smtplib.SSLFakeFile': 'smtplib.SSLFakeFile is moved in Python 3. Use socket.socket.makefile instead',
        'SocketServer': 'SocketServer is moved in Python3. six.moves.socketserver can be used as a drop-in replacement.',  # noqa:E501
        'sre': 'sre is moved in Python 3. Use re instead',
        'statvfs': 'statvfs is moved in Python 3. Use os.statvfs instead',
        'string.atof': 'string.atof is moved in Python3. float can be used as a drop-in replacement.',
        'string.atoi': 'string.atoi is moved in Python3. int can be used as a drop-in replacement.',
        'string.atol': 'string.atol is moved in Python3. int can be used as a drop-in replacement.',
        'string.capitalize': 'string.capitalize is removed in Python 3.',
        'string.center': 'string.center is removed in Python 3.',
        'string.count': 'string.count is removed in Python 3.',
        'string.expandtabs': 'string.expandtabs is removed in Python 3.',
        'string.find': 'string.find is removed in Python 3.',
        'string.index': 'string.index is removed in Python 3.',
        'string.join': 'string.join is removed in Python 3.',
        'string.joinfields': 'string.joinfields is removed in Python 3.',
        'string.letters': 'string.letters is moved in Python3. string.ascii_letters can be used as a drop-in replacement.',  # noqa:E501
        'string.ljust': 'string.ljust is removed in Python 3.',
        'string.lower': 'string.lower is removed in Python 3.',
        'string.lowercase': 'string.lowercase is moved in Python3. string.ascii_lowercase can be used as a drop-in replacement.',  # noqa:E501
        'string.lstrip': 'string.lstrip is removed in Python 3.',
        'string.maketrans': 'string.maketrans is moved in Python 3. Use bytes.maketrans/bytearray.maketrans or a dict of unicode codepoints to substitutions instead',  # noqa:E501
        'string.replace': 'string.replace is removed in Python 3.',
        'string.rfind': 'string.rfind is removed in Python 3.',
        'string.rindex': 'string.rindex is removed in Python 3.',
        'string.rjust': 'string.rjust is removed in Python 3.',
        'string.rsplit': 'string.rsplit is removed in Python 3.',
        'string.rstrip': 'string.rstrip is removed in Python 3.',
        'string.split': 'string.split is removed in Python 3.',
        'string.splitfields': 'string.splitfields is removed in Python 3.',
        'string.strip': 'string.strip is removed in Python 3.',
        'string.swapcase': 'string.swapcase is removed in Python 3.',
        'string.translate': 'string.translate is removed in Python 3.',
        'string.upper': 'string.upper is removed in Python 3.',
        'string.uppercase': 'string.uppercase is moved in Python3. string.ascii_uppercase can be used as a drop-in replacement.',  # noqa:E501
        'string.zfill': 'string.zfill is removed in Python 3.',
        'StringIO': 'StringIO is moved in Python 3. Use io.StringIO or io.BytesIO instead',
        'stringold': 'stringold is removed in Python 3.',
        'sunaudio': 'sunaudio is removed in Python 3.',
        'sv': 'sv is removed in Python 3.',
        'tarfile.S_IFBLK': 'tarfile.S_IFBLK is moved in Python3. stat.S_IFBLK can be used as a drop-in replacement.',
        'tarfile.S_IFCHR': 'tarfile.S_IFCHR is moved in Python3. stat.S_IFCHR can be used as a drop-in replacement.',
        'tarfile.S_IFDIR': 'tarfile.S_IFDIR is moved in Python3. stat.S_IFDIR can be used as a drop-in replacement.',
        'tarfile.S_IFIFO': 'tarfile.S_IFIFO is moved in Python3. stat.S_IFIFO can be used as a drop-in replacement.',
        'tarfile.S_IFLNK': 'tarfile.S_IFLNK is moved in Python3. stat.S_IFLNK can be used as a drop-in replacement.',
        'tarfile.S_IFREG': 'tarfile.S_IFREG is moved in Python3. stat.S_IFREG can be used as a drop-in replacement.',
        'test.test_support': 'test.test_support is moved in Python 3. Use test.support instead',
        'test.testall': 'test.testall is removed in Python 3.',
        'thread': 'thread is moved in Python3. six.moves._thread can be used as a drop-in replacement.',
        'time.accept2dyear': 'time.accept2dyear is removed in Python 3.',
        'timing': 'timing is moved in Python 3. Use time.clock instead',
        'Tix': 'Tix is moved in Python3. six.moves.tkinter_tix can be used as a drop-in replacement.',
        'tkColorChooser': 'tkColorChooser is moved in Python3. six.moves.tkinter_colorchooser can be used as a drop-in replacement.',  # noqa:E501
        'tkCommonDialog': 'tkCommonDialog is moved in Python3. six.moves.tkinter_commondialog can be used as a drop-in replacement.',  # noqa:E501
        'Tkconstants': 'Tkconstants is moved in Python3. six.moves.tkinter_constants can be used as a drop-in replacement.',  # noqa:E501
        'Tkdnd': 'Tkdnd is moved in Python3. six.moves.tkinter_dnd can be used as a drop-in replacement.',
        'tkFileDialog': 'tkFileDialog is moved in Python3. six.moves.tkinter_tkfiledialog can be used as a drop-in replacement.',  # noqa:E501
        'tkFont': 'tkFont is moved in Python3. six.moves.tkinter_font can be used as a drop-in replacement.',
        'Tkinter': 'Tkinter is moved in Python3. six.moves.tkinter can be used as a drop-in replacement.',
        'tkMessageBox': 'tkMessageBox is moved in Python3. six.moves.tkinter_messagebox can be used as a drop-in replacement.',  # noqa:E501
        'tkSimpleDialog': 'tkSimpleDialog is moved in Python3. six.moves.tkinter_tksimpledialog can be used as a drop-in replacement.',  # noqa:E501
        'toaiff': 'toaiff is removed in Python 3.',
        'ttk': 'ttk is moved in Python3. six.moves.tkinter_ttk can be used as a drop-in replacement.',
        'types.BooleanType': 'types.BooleanType is moved in Python3. bool can be used as a drop-in replacement.',
        'types.BufferType': 'types.BufferType is removed in Python 3.',
        'types.ClassType': 'types.ClassType is removed in Python 3.',
        'types.ComplexType': 'types.ComplexType is moved in Python3. complex can be used as a drop-in replacement.',
        'types.DictionaryType': 'types.DictionaryType is removed in Python 3.',
        'types.DictProxyType': 'types.DictProxyType is removed in Python 3.',
        'types.DictType': 'types.DictType is moved in Python3. dict can be used as a drop-in replacement.',
        'types.EllipsisType': 'types.EllipsisType is moved in Python3. type(Ellipsis) can be used as a drop-in replacement.',  # noqa:E501
        'types.FileType': 'types.FileType is removed in Python 3.',
        'types.FloatType': 'types.FloatType is moved in Python3. float can be used as a drop-in replacement.',
        'types.InstanceType': 'types.InstanceType is removed in Python 3.',
        'types.IntType': 'types.IntType is moved in Python3. six.integer_types can be used as a drop-in replacement.',
        'types.ListType': 'types.ListType is moved in Python3. list can be used as a drop-in replacement.',
        'types.LongType': 'types.LongType is removed in Python 3.',
        'types.NoneType': 'types.NoneType is moved in Python3. type(None) can be used as a drop-in replacement.',
        'types.NotImplementedType': 'types.NotImplementedType is removed in Python 3.',
        'types.ObjectType': 'types.ObjectType is removed in Python 3.',
        'types.SliceType': 'types.SliceType is removed in Python 3.',
        'types.StringType': 'types.StringType is moved in Python 3. Use six.binary_types or six.text_types depdending on context instead',  # noqa:E501
        'types.StringTypes': 'types.StringTypes is moved in Python3. six.string_types can be used as a drop-in replacement.',  # noqa:E501
        'types.TupleType': 'types.TupleType is moved in Python3. tuple can be used as a drop-in replacement.',
        'types.TypeType': 'types.TypeType is moved in Python3. six.class_types can be used as a drop-in replacement.',
        'types.UnboundMethodType': 'types.UnboundMethodType is removed in Python 3.',
        'types.UnicodeType': 'types.UnicodeType is moved in Python3. six.text_type can be used as a drop-in replacement.',  # noqa:E501
        'types.XRangeType': 'types.XRangeType is removed in Python 3.',
        'urllib.ContentTooShortError': 'urllib.ContentTooShortError is moved in Python3. six.moves.urllib.error.ContentTooShortError can be used as a drop-in replacement.',  # noqa:E501
        'urllib.FancyURLopener': 'urllib.FancyURLopener is moved in Python3. six.moves.urllib.request.FancyURLopener can be used as a drop-in replacement.',  # noqa:E501
        'urllib.getproxies': 'urllib.getproxies is moved in Python3. six.moves.urllib.request.getproxies can be used as a drop-in replacement.',  # noqa:E501
        'urllib.pathname2url': 'urllib.pathname2url is moved in Python3. six.moves.urllib.request.pathname2url can be used as a drop-in replacement.',  # noqa:E501
        'urllib.proxy_bypass': 'urllib.proxy_bypass is moved in Python3. six.moves.urllib.request.proxy_bypass can be used as a drop-in replacement.',  # noqa:E501
        'urllib.quote': 'urllib.quote is moved in Python3. six.moves.urllib.parse.quote can be used as a drop-in replacement.',  # noqa:E501
        'urllib.quote_plus': 'urllib.quote_plus is moved in Python3. six.moves.urllib.parse.quote_plus can be used as a drop-in replacement.',  # noqa:E501
        'urllib.splitquery': 'urllib.splitquery is moved in Python3. six.moves.urllib.parse.splitquery can be used as a drop-in replacement.',  # noqa:E501
        'urllib.splittag': 'urllib.splittag is moved in Python3. six.moves.urllib.parse.splittag can be used as a drop-in replacement.',  # noqa:E501
        'urllib.splituser': 'urllib.splituser is moved in Python3. six.moves.urllib.parse.splituser can be used as a drop-in replacement.',  # noqa:E501
        'urllib.unquote': 'urllib.unquote is moved in Python3. six.moves.urllib.parse.unquote can be used as a drop-in replacement.',  # noqa:E501
        'urllib.unquote_plus': 'urllib.unquote_plus is moved in Python3. six.moves.urllib.parse.unquote_plus can be used as a drop-in replacement.',  # noqa:E501
        'urllib.url2pathname': 'urllib.url2pathname is moved in Python3. six.moves.urllib.request.url2pathname can be used as a drop-in replacement.',  # noqa:E501
        'urllib.urlcleanup': 'urllib.urlcleanup is moved in Python3. six.moves.urllib.request.urlcleanup can be used as a drop-in replacement.',  # noqa:E501
        'urllib.urlencode': 'urllib.urlencode is moved in Python3. six.moves.urllib.parse.urlencode can be used as a drop-in replacement.',  # noqa:E501
        'urllib.URLopener': 'urllib.URLopener is moved in Python3. six.moves.urllib.request.URLopener can be used as a drop-in replacement.',  # noqa:E501
        'urllib.urlretrieve': 'urllib.urlretrieve is moved in Python3. six.moves.urllib.request.urlretrieve can be used as a drop-in replacement.',  # noqa:E501
        'urllib2': 'urllib2 is moved in Python 3. Use six.moves.urllib instead',
        'urllib2.AbstractBasicAuthHandler': 'urllib2.AbstractBasicAuthHandler is moved in Python3. six.moves.urllib.request.AbstractBasicAuthHandler can be used as a drop-in replacement.',  # noqa:E501
        'urllib2.AbstractDigestAuthHandler': 'urllib2.AbstractDigestAuthHandler is moved in Python3. six.moves.urllib.request.AbstractDigestAuthHandler can be used as a drop-in replacement.',  # noqa:E501
        'urllib2.BaseHandler': 'urllib2.BaseHandler is moved in Python3. six.moves.urllib.request.BaseHandler can be used as a drop-in replacement.',  # noqa:E501
        'urllib2.build_opener': 'urllib2.build_opener is moved in Python3. six.moves.urllib.request.build_opener can be used as a drop-in replacement.',  # noqa:E501
        'urllib2.CacheFTPHandler': 'urllib2.CacheFTPHandler is moved in Python3. six.moves.urllib.request.CacheFTPHandler can be used as a drop-in replacement.',  # noqa:E501
        'urllib2.FileHandler': 'urllib2.FileHandler is moved in Python3. six.moves.urllib.request.FileHandler can be used as a drop-in replacement.',  # noqa:E501
        'urllib2.FTPHandler': 'urllib2.FTPHandler is moved in Python3. six.moves.urllib.request.FTPHandler can be used as a drop-in replacement.',  # noqa:E501
        'urllib2.HTTPBasicAuthHandler': 'urllib2.HTTPBasicAuthHandler is moved in Python3. six.moves.urllib.request.HTTPBasicAuthHandler can be used as a drop-in replacement.',  # noqa:E501
        'urllib2.HTTPCookieProcessor': 'urllib2.HTTPCookieProcessor is moved in Python3. six.moves.urllib.request.HTTPCookieProcessor can be used as a drop-in replacement.',  # noqa:E501
        'urllib2.HTTPDefaultErrorHandler': 'urllib2.HTTPDefaultErrorHandler is moved in Python3. six.moves.urllib.request.HTTPDefaultErrorHandler can be used as a drop-in replacement.',  # noqa:E501
        'urllib2.HTTPDigestAuthHandler': 'urllib2.HTTPDigestAuthHandler is moved in Python3. six.moves.urllib.request.HTTPDigestAuthHandler can be used as a drop-in replacement.',  # noqa:E501
        'urllib2.HTTPError': 'urllib2.HTTPError is moved in Python3. six.moves.urllib.error.HTTPError can be used as a drop-in replacement.',  # noqa:E501
        'urllib2.HTTPErrorProcessor': 'urllib2.HTTPErrorProcessor is moved in Python3. six.moves.urllib.request.HTTPErrorProcessor can be used as a drop-in replacement.',  # noqa:E501
        'urllib2.HTTPHandler': 'urllib2.HTTPHandler is moved in Python3. six.moves.urllib.request.HTTPHandler can be used as a drop-in replacement.',  # noqa:E501
        'urllib2.HTTPPasswordMgr': 'urllib2.HTTPPasswordMgr is moved in Python3. six.moves.urllib.request.HTTPPasswordMgr can be used as a drop-in replacement.',  # noqa:E501
        'urllib2.HTTPPasswordMgrWithDefaultRealm': 'urllib2.HTTPPasswordMgrWithDefaultRealm is moved in Python3. six.moves.urllib.request.HTTPPasswordMgrWithDefaultRealm can be used as a drop-in replacement.',  # noqa:E501
        'urllib2.HTTPRedirectHandler': 'urllib2.HTTPRedirectHandler is moved in Python3. six.moves.urllib.request.HTTPRedirectHandler can be used as a drop-in replacement.',  # noqa:E501
        'urllib2.HTTPSHandler': 'urllib2.HTTPSHandler is moved in Python3. six.moves.urllib.request.HTTPSHandler can be used as a drop-in replacement.',  # noqa:E501
        'urllib2.install_opener': 'urllib2.install_opener is moved in Python3. six.moves.urllib.request.install_opener can be used as a drop-in replacement.',  # noqa:E501
        'urllib2.OpenerDirector': 'urllib2.OpenerDirector is moved in Python3. six.moves.urllib.request.OpenerDirector can be used as a drop-in replacement.',  # noqa:E501
        'urllib2.ProxyBasicAuthHandler': 'urllib2.ProxyBasicAuthHandler is moved in Python3. six.moves.urllib.request.ProxyBasicAuthHandler can be used as a drop-in replacement.',  # noqa:E501
        'urllib2.ProxyDigestAuthHandler': 'urllib2.ProxyDigestAuthHandler is moved in Python3. six.moves.urllib.request.ProxyDigestAuthHandler can be used as a drop-in replacement.',  # noqa:E501
        'urllib2.ProxyHandler': 'urllib2.ProxyHandler is moved in Python3. six.moves.urllib.request.ProxyHandler can be used as a drop-in replacement.',  # noqa:E501
        'urllib2.Request': 'urllib2.Request is moved in Python3. six.moves.urllib.request.Request can be used as a drop-in replacement.',  # noqa:E501
        'urllib2.UnknownHandler': 'urllib2.UnknownHandler is moved in Python3. six.moves.urllib.request.UnknownHandler can be used as a drop-in replacement.',  # noqa:E501
        'urllib2.URLError': 'urllib2.URLError is moved in Python3. six.moves.urllib.error.URLError can be used as a drop-in replacement.',  # noqa:E501
        'urllib2.urlopen': 'urllib2.urlopen is moved in Python3. six.moves.urllib.request.urlopen can be used as a drop-in replacement.',  # noqa:E501
        'urlparse': 'urlparse is moved in Python 3. Use six.moves.parse instead',
        'urlparse.parse_qs': 'urlparse.parse_qs is moved in Python3. six.moves.urllib.parse.parse_qs can be used as a drop-in replacement.',  # noqa:E501
        'urlparse.parse_qsl': 'urlparse.parse_qsl is moved in Python3. six.moves.urllib.parse.parse_qsl can be used as a drop-in replacement.',  # noqa:E501
        'urlparse.ParseResult': 'urlparse.ParseResult is moved in Python3. six.moves.urllib.parse.ParseResult can be used as a drop-in replacement.',  # noqa:E501
        'urlparse.SplitResult': 'urlparse.SplitResult is moved in Python3. six.moves.urllib.parse.SplitResult can be used as a drop-in replacement.',  # noqa:E501
        'urlparse.urldefrag': 'urlparse.urldefrag is moved in Python3. six.moves.urllib.parse.urldefrag can be used as a drop-in replacement.',  # noqa:E501
        'urlparse.urljoin': 'urlparse.urljoin is moved in Python3. six.moves.urllib.parse.urljoin can be used as a drop-in replacement.',  # noqa:E501
        'urlparse.urlparse': 'urlparse.urlparse is moved in Python3. six.moves.urllib.parse.urlparse can be used as a drop-in replacement.',  # noqa:E501
        'urlparse.urlsplit': 'urlparse.urlsplit is moved in Python3. six.moves.urllib.parse.urlsplit can be used as a drop-in replacement.',  # noqa:E501
        'urlparse.urlunparse': 'urlparse.urlunparse is moved in Python3. six.moves.urllib.parse.urlunparse can be used as a drop-in replacement.',  # noqa:E501
        'urlparse.urlunsplit': 'urlparse.urlunsplit is moved in Python3. six.moves.urllib.parse.urlunsplit can be used as a drop-in replacement.',  # noqa:E501
        'urlparse.uses_fragment': 'urlparse.uses_fragment is moved in Python3. six.moves.urllib.parse.uses_fragment can be used as a drop-in replacement.',  # noqa:E501
        'urlparse.uses_netloc': 'urlparse.uses_netloc is moved in Python3. six.moves.urllib.parse.uses_netloc can be used as a drop-in replacement.',  # noqa:E501
        'urlparse.uses_params': 'urlparse.uses_params is moved in Python3. six.moves.urllib.parse.uses_params can be used as a drop-in replacement.',  # noqa:E501
        'urlparse.uses_query': 'urlparse.uses_query is moved in Python3. six.moves.urllib.parse.uses_query can be used as a drop-in replacement.',  # noqa:E501
        'urlparse.uses_relative': 'urlparse.uses_relative is moved in Python3. six.moves.urllib.parse.uses_relative can be used as a drop-in replacement.',  # noqa:E501
        'user': 'user is removed in Python 3.',
        'UserDict': 'UserDict is moved in Python 3. Use dict or collections.UserDict/collections.MutableMapping instead',  # noqa:E501
        'UserDict.UserDict': 'UserDict.UserDict is moved in Python3. six.moves.UserDict can be used as a drop-in replacement.',  # noqa:E501
        'UserDict.UserDictMixin': 'UserDict.UserDictMixin is moved in Python 3. Use collections.MutableMapping instead',  # noqa:E501
        'UserList': 'UserList is moved in Python 3. Use list or collections.UserList/collections.MutableSequence instead',  # noqa:E501
        'UserList.UserList': 'UserList.UserList is moved in Python3. six.moves.UserList can be used as a drop-in replacement.',  # noqa:E501
        'UserString': 'UserString is moved in Python 3. Use six.text_type, six.binary_type or collections.UserString instead',  # noqa:E501
        'UserString.UserString': 'UserString.UserString is moved in Python3. six.moves.UserString can be used as a drop-in replacement.',  # noqa:E501
        'xmlrpclib': 'xmlrpclib is moved in Python3. six.moves.xmlrpc_client can be used as a drop-in replacement.',
    }
