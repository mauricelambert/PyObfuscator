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

## Attributes and super Error

Becareful with attribute name and definition !

Your attributes must be defined as attributes and your attributes functions mustn't have same name than attributes function defined in different files !

With the `super` function your must add `self.class` and `self` as arguments (without consequences).

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
        #"self.abc" ## THIS LINE RETURN AN ERROR (because "abc" is not define as attribute, the name will be obfuscate)
        self.abc2 ## this line doesn't return an error (because "self.abc2" is defined as attribute)
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

## Links
 - [Github Page](https://github.com/mauricelambert/PyObfuscator/)
 - [Documentation](https://mauricelambert.github.io/info/python/security/PyObfuscator.html)
 - [Download as python executable](https://mauricelambert.github.io/info/python/security/PyObfuscator.pyz)
 - [Pypi package](https://pypi.org/project/PyObfuscator/)
 - [Demo](https://github.com/mauricelambert/PyObfuscator/tree/main/Demo)

## Licence
Licensed under the [GPL, version 3](https://www.gnu.org/licenses/).