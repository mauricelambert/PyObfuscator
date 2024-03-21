from urllib.request import urlopen as req2
import xml.dom as mydom
from xml.dom import minicompat
import xml.dom.minidom
import os.path
import builtins
try:
    import other
except:
    # from . import other
    other2 = __import__("other2", globals=globals(), locals=locals(), level=1)

try:
    import other2
except:
    # from . import other2
    other2 = __import__("other2", globals=globals(), locals=locals(), level=1)

req2("file:///etc/passwd")
mydom.XML_NAMESPACE
minicompat.__file__
xml.dom.minidom.Attr
builtins.print('abc')
print(os.path.join('test', 'abc'))
print(other.test)
print(other2.test2)
