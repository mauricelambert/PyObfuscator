# PyObfuscator

## Description
This package implement a python code Obfuscator.

## Requirements
This package require :
 - python3.9 or greater
 - python3.9 or greater Standard Library

## Installation
```bash
pip install PyObfuscator
```

## Usages

## Command line:
```bash
PyObfuscator -h # help message
PyObfuscator code.py # easiest command
PyObfuscator -o "obfu.py" -l 6 -n "name1:obfu_name1" "name2:obfu_name2" -n "name3:obfu_name3" -d -w "mypassword" -e "utf-8" -s 8 -p -g 50 -f "logs.log" code.py
```

### Python script
```python
from PyObfuscator import Obfuscator, Name
Obfuscator('code.py').default_obfuscation() # write your obfuscate code in code_obfu.py

Obfuscator(
    "code.py",
    "obfu.py",
    6,
    {
        "name1": Name("name1", "obfu_name1", False, None),
        "name2": Name("name2", "obfu_name2", False, None),
        "name3": Name("name3", "obfu_name3", False, None),
    },
    True,
    "mypassword",
    "utf-8",
    8,
).default_obfuscation()
```

### Python executable:
```bash
python3 PyObfuscator.pyz -o "obfu.py" -l 6 -n "name1:obfu_name1" "name2:obfu_name2" -n "name3:obfu_name3" -d -w "mypassword" -e "utf-8" -s 8 -p -g 50 -f "logs.log" code.py

# OR
chmod u+x PyObfuscator.pyz # add execute rights
./PyObfuscator.pyz code.py # execute file
```

### Python module (command line):

```bash
python3 -m PyObfuscator -o "obfu.py" -l 6 -n "name1:obfu_name1" "name2:obfu_name2" -n "name3:obfu_name3" -d -w "mypassword" -e "utf-8" -s 8 -p -g 50 -f "logs.log" code.py
python3 -m PyObfuscator.Obfuscator code.py
```

## Tests

```bash
cd tests
python3 -m unittest discover
```

## Bugs and python errors

### Class
Becareful with attribute name and definition !

Your attributes must be defined as attributes and your attributes functions mustn't have same name than attributes function defined in different files !

With the `super` function your must add `self.__class__` and `self` as arguments (no consequences).

```python
class Classe:
    abc: str = "abc"
class Classe2(Classe):
    def __init__(self):
        self.abc2: str = "abc"
class Test(Classe2):
    def __init__(self, string: str):
        #super().__init__() ## THIS LINE RETURN AN ERROR
        super(self.__class__, self).__init__() ## this line doesn't return an error
        #print(self.abc) ## THIS LINE RETURN AN ERROR (because "abc" is not define as attribute, the name will be obfuscate)
        print(self.abc2) ## this line doesn't return an error (because "self.abc2" is defined as attribute)
```

```python
import module
class Classe:
	def __init__(self):
		self.attr
	def function():
		pass
Classe.function() # This line will be obfuscate (this line is safe)
module.function() ## THIS LINE RETURN AN ERROR (because "function" attribute will be obfuscate (only for function attributes))
module.attr # this line is safe (because "attr" is not function)
```

### Import

I recommend you to use the first import but i propose you alternative soluce to solve this bug.
```python
import urllib.request as urllib
urllib.request.urlopen("https://www.python.org/") # This line is safe
import os.path as os
print(os.path.exists("test")) # This line is safe
```

```python
import urllib
urllib.request.urlopen("https://www.python.org/") ## THIS LINE RETURN AN ERROR (because request is not in file named "urllib/__init__.py")
import os
print(os.path.exists("test")) # This line is safe (because path is define in file named "os.py")
```

```python
from urllib import request
request.urlopen("https://www.python.org/") ## THIS LINE RETURN AN ERROR
# KeyError: 'request'
from os import path
print(path.exists("test")) # This line is safe
```

```python
from urllib.request import urlopen
urlopen("https://www.python.org/") ## THIS LINE RETURN AN ERROR
# KeyError: 'urlopen'
from os.path import exists
print(exists("test")) ## THIS LINE RETURN AN ERROR
# KeyError: 'exists'
```

```python
import urllib.request
urllib.request.urlopen("https://www.python.org/") ## THIS LINE RETURN AN ERROR
# NameError: name 'dmJQL9VsPms3' is not defined
import os.path as os
print(os.path.exists("test")) # This line is safe
```

#### Solve this bug

I do not recommend using this solution because other packages may import the module in a different way and return this error:

```
ImportError: cannot import name '_has_surrogates' from partially initialized module 'email.utils' (most likely due to a circular import) (/lib/email/utils.py)
```

##### Linux

Run this script bash:
```bash
cp -r $(python3 -c "import urllib,os;print(os.path.dirname(urllib.__file__))") .
cd urllib
python3 -c "import glob;[(open('__init__.py','a',encoding='utf-8').write(f'from . import {f[:-3]}\n'),t:=open(f,encoding='utf-8').read(),open(f,'w',encoding='utf-8').write(t.replace('import urllib.', 'from . import ').replace('from urllib.', 'from .').replace('urllib.', ''))) for f in glob.iglob('*') if not (f.startswith('__') and (f.endswith('__.py') or f.endswith('__')))]"
```

##### Windows

Run this script batch:
```bash
mkdir urllib
python -c "import urllib,os;print(os.path.dirname(urllib.__file__))">temp.txt
set /p lib=<temp.txt
copy "%lib%" urllib
del temp.txt
cd urllib
python -c "import glob;[(open('__init__.py','a',encoding='utf-8').write(f'from . import {f[:-3]}\n'),t:=open(f,encoding='utf-8').read(),open(f,'w',encoding='utf-8').write(t.replace('import urllib.', 'from . import ').replace('from urllib.', 'from .').replace('urllib.', ''))) for f in glob.iglob('*') if not (f.startswith('__') and (f.endswith('__.py') or f.endswith('__')))]"
```

### Pyinstaller

Be careful with pyinstaller or other way to freeze your app, somes variables exist in the default python interpreter but not in your freezed app. Set variables with default values to solve error (for pyinstaller):

```python
copyright="""Copyright (c) 2001-2021 Python Software Foundation.
All Rights Reserved.

Copyright (c) 2000 BeOpen.com.
All Rights Reserved.

Copyright (c) 1995-2001 Corporation for National Research Initiatives.
All Rights Reserved.

Copyright (c) 1991-1995 Stichting Mathematisch Centrum, Amsterdam.
All Rights Reserved."""
credits="""    Thanks to CWI, CNRI, BeOpen.com, Zope Corporation and a cast of thousands
    for supporting Python development.  See www.python.org for more information."""
help="Type help() for interactive help, or help(object) for help about object."
quit="Use quit() or Ctrl-Z plus Return to exit"
license="Type license() to see the full license text"
__cached__=""
```

## Links
 - [Github Page](https://github.com/mauricelambert/PyObfuscator/)
 - [Documentation](https://mauricelambert.github.io/info/python/security/PyObfuscator.html)
 - [Download as python executable](https://mauricelambert.github.io/info/python/security/PyObfuscator.pyz)
 - [Pypi package](https://pypi.org/project/PyObfuscator/)
 - [Demo](https://github.com/mauricelambert/PyObfuscator/tree/main/Demo)

## Licence
Licensed under the [GPL, version 3](https://www.gnu.org/licenses/).
