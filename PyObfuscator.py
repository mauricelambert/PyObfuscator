#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    This module obfuscates python code.
#    Copyright (C) 2021, 2022, 2023, 2024  Maurice Lambert

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
###################

"""
This module obfuscates python code.

>>> with open("code.py", "w") as f: n = f.write("print('Hello world !')")
>>> Obfuscator("code.py", deobfuscate=False).default_obfuscation()
>>> with open("code_obfu.py") as f: exec(f.read())
Hello world !
>>> from os import remove; remove("code.py"); remove("code_obfu.py")

Tests:
 - python3.11 -m doctest -v PyObfuscator.py
    22 tests in 58 items.
    22 passed and 0 failed.
    Test passed.
 - python3.11 -m unittest discover -s tests -p Test*.py -v
    ................................
    ----------------------------------------------------------------------
    Ran 39 tests in 0.150s
    OK
 - python3.11 -m coverage report
    Name                        Stmts   Miss  Cover
    -----------------------------------------------
    PyObfuscator.py               400      1    99%
    -----------------------------------------------
    TOTAL                         400      1    99%

"""

default_dir = dir()

__version__ = "0.1.7"
__author__ = "Maurice Lambert"
__author_email__ = "mauricelambert434@gmail.com"
__maintainer__ = "Maurice Lambert"
__maintainer_email__ = "mauricelambert434@gmail.com"
__description__ = "This module obfuscates python code."
license = "GPL-3.0 License"
__url__ = "https://github.com/mauricelambert/PyObfuscator/"

copyright = """
PyObfuscator  Copyright (C) 2021, 2022, 2023, 2024  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
"""
__license__ = license
__copyright__ = copyright

__all__ = [
    "Obfuscator",
    "main",
    "Name",
    "DocPassword",
    "DocLevels",
]

print(copyright)

from ast import (
    AST,
    Attribute,
    Call,
    Tuple as TupleAst,
    Load,
    Constant,
    Import,
    ImportFrom,
    AugAssign,
    AnnAssign,
    Assign,
    Module,
    Store,
    Name as NameAst,
    NodeTransformer,
    JoinedStr,
    Expr,
    ClassDef,
    FunctionDef,
    AsyncFunctionDef,
    ExceptHandler,
    Global,
    alias,
    arg,
    parse,
    unparse,
)
from argparse import ArgumentParser, Namespace
from logging import debug, info, basicConfig
from random import choice, choices, randint
from string import ascii_letters, digits
from typing import Tuple, Dict, List
from dataclasses import dataclass
from os.path import splitext
from base64 import b85encode
from re import sub, finditer
from gzip import compress
from json import dump
import builtins


class DocPassword:

    """
    Password is a string to encrypt python code with xor.

    if password is None:
        - random password is define and write in python file
        code is independent but it's easy to reverse this obfuscation
    if password is a string:
        - password is not written in python file, to run
        the code you must enter the password (console mode)

    Note: this password is not use if you don't use
    Obfuscator.xor function or Level is less than 4.
    """

    def print_the_doc() -> None:
        print(DocPassword.__doc__)


class DocLevels:
    r"""
    Level is an integer to define obfuscation level.

    if level equal 1:
        - variable name change (using Obfuscator.change_variables_name function)
            variables is less understandable
        - doc and signature is deleted
            function, class
    if level equal 2:
        - level 1
        - strings are encrypted (using Obfuscator.crypt_strings function)
            the strings become illegible but execution is longer
    if level equal 3:
        - level 2
        - code is compressed using GZIP
            the code structure becomes invisible but execution is longer
    if level equal 4:
        - level 3
        - encrypt the code but execution is longer
    if level equal 5:
        - level 4
        - encode code using base85
            bigger file size and execution is longer
    if level equal 6:
        - level 5
        - encode your code as hexadecimal escape ('a' become '\x061')
            file size * 4
    """

    def print_the_doc() -> None:
        print(DocLevels.__doc__)


@dataclass
class Name:

    """
    Dataclass with default name, obfuscation name, definition and namespace.

    name(str): default variable name
    obfuscation(str): variable name after obfuscation (a random name)
    is_defined(bool): a boolean representing the definition in file
    namespace_name(str): the namespace (None or <class name> or <class name>.<function name>)
    """

    name: str
    obfuscation: str
    is_defined: bool
    namespace_name: str


@dataclass
class ModuleImport:

    """
    This dataclass contains modules informations to import it.
    """

    name: str
    alias: str


@dataclass
class ElementImport:

    """
    This dataclass contains name to import it from module.
    """

    name: str
    asname: str


class Obfuscator(NodeTransformer):

    """
    This class obfuscates python code.

    filename(str):                 python filename to obfuscate
    output_filename(str) = None:   obfuscate python filename
    level(int) = 6:                obfuscation level (see DocLevels)
    names(Dict[str, Name]) = {}:   names you need to know (define your obfuscation names for import)
        For exemple: to import class named 'Obfuscator' as 'Fdg6jsT_2', names must be
        "{'Obfuscator': Name('Obfuscator', 'Fdg6jsT_2', False, None)}".
    deobfuscate(bool) = True:      save names in a JSON file to reverse name obfuscation
    password(str) = None:          key for encryption (see DocPassword)
    encoding(str) = 'utf-8':       python file encoding
    names_size(int) = 12:          size to generate random variables names
    """

    def __init__(
        self,
        filename: str,
        output_filename: str = None,
        level: int = 6,
        names: Dict[str, Name] = {},
        deobfuscate: bool = True,
        password: str = None,
        encoding: str = "utf-8",
        names_size: int = 12,
    ):
        self.filename = filename
        self.output_filename = output_filename or f"{splitext(filename)[0]}_obfu.py"
        self.level = level
        self.deobfuscate = deobfuscate

        self.password = password
        self.code = None
        self.astcode = None

        self.default_names = names
        self.obfu_names = {v.obfuscation: v for v in names.values()}

        self.names_size = names_size
        self.encoding = encoding

        self._xor_password_key = None
        self._xor_password_key_length = 40

        self.current_class = None
        self.default_is_define = False

        self.using_default_obfu = False

        self.in_format_string = False
        self.hard_coded_string = {("decode",), ("utf-8",)}

        super().__init__()

    def get_random_name(self, first_name: str, is_defined: bool = False) -> Name:
        """
        This function returns a random variable name.

        >>> Obfuscator("").get_random_name("test").name
        'test'
        >>>
        """

        if (name := self.default_names.get(first_name)) is not None:
            return name

        while name is None or name in self.obfu_names.keys():
            first = choice("_" + ascii_letters)
            name = "".join(choices("_" + ascii_letters + digits, k=self.names_size - 1))

            name = first + name

        name = Name(
            first_name,
            name,
            is_defined or self.default_is_define,
            self.current_class,
        )
        self.obfu_names[name.obfuscation] = name
        self.default_names[first_name] = name

        return name

    def get_code(self) -> Tuple[str, AST]:
        """
        This function returns content and AST from python file.
        """

        with open(self.filename, encoding=self.encoding) as file:
            code = self.code = file.read()

        debug(f"Get code from {self.filename!r}")

        astcode = self.astcode = parse(code)
        return code, astcode

    def add_super_arguments(self, code: str = None) -> Tuple[str, AST]:
        r"""
        This function adds super arguments because super
        can't defined it's arguments after obfuscation.

        >>> code = "class A:\n\tdef __init__(self):super().__init__()"
        >>> code, _ = Obfuscator("").add_super_arguments(code)
        >>> code
        'class A:\n\tdef __init__(self):super(self.__class__, self).__init__()'
        >>>
        """

        code = self.code = sub(
            r"\bsuper\b\(\)",
            "super(self.__class__, self)",
            (code or self.code),
        )

        astcode = self.astcode = parse(code)
        info("Super arguments is added.")
        return code, astcode

    def add_builtins(self) -> str:
        """
        This function adds builtins obfuscation on the top of the code
        and returns it.

        This function raises RuntimeError if builtins are not obfuscate.

        This function raises RuntimeError if self.code is None.
        """

        if (init := getattr(self, "default_variables", None)) is None:
            raise RuntimeError("Initialize obfuscation with 'init_builtins' method.")

        if self.code is None:
            raise RuntimeError("Code is not defined")

        code = self.code = f"{init}{self.code}"
        return code

    def write_code(self) -> Tuple[str, AST]:
        """
        This function writes obfuscate code in output file
        and returns the obfuscate code.

        This function raises RuntimeError if self.code is None.
        """

        code = self.code
        if code is None:
            raise RuntimeError("Code is not defined")

        with open(self.output_filename, "w", encoding=self.encoding) as file:
            file.write(code)

        debug(f"Write obfuscate code in {self.output_filename}")

        return code

    def gzip(self, code: str = None) -> str:
        """
        This function compress python code with gzip.
           (Level 3)

        - if code is None this function use self.code
        - self.code is compressed using GZIP
        - returns the compressed code

        >>> code = "print('Hello World !')"
        >>> obfu = Obfuscator("").gzip(code)
        >>> code != obfu
        True
        >>> exec(obfu)
        Hello World !
        >>>
        """

        code = code or self.code

        if self.level >= 3:
            code = compress(code.encode())
            self.code = code = f"from gzip import decompress as __;_=exec;_(__({code}))"
            debug("Code is compressed using gzip.")

        return code

    def hexadecimal(self, code: str = None) -> str:
        r"""
        This function encodes python code as hexadecimal ('a' become '\x61').
           (Level 6)

        - if code is None this function use self.code
        - self.code is encoded as hexadecimal
        - returns the hexadecimal encoded code

        >>> code = "print('Hello World !')"
        >>> obfu = Obfuscator("").hexadecimal(code)
        >>> code != obfu
        True
        >>> exec(obfu)
        Hello World !
        >>>
        """

        code = code or self.code

        if self.level >= 6:
            code = "".join([f"\\x{car:0>2x}" for car in code.encode()])
            code = self.code = f"_=exec;_('{code}')"
            debug("Code is encoded as hexadecimal.")

        return code

    def xor_code(self, code: str = None, password: str = None) -> str:
        """
        This function encrypts code using xor.
           (Level 4)

        - if code is None this function use self.code
        - if password is None this function use self.password
               (see the DocPassword's doc string for more information)
        - if self.password is None this function generate a random password
               (see the DocPassword's doc string for more information)
        - self.code is set to encrypted code
        - returns the encrypted code

        >>> exec(Obfuscator("").xor_code("print('Hello World !')"))
        Hello World !
        >>>
        """

        code = code or self.code
        if self.level < 4:
            return code

        password = password or self.password
        if password:
            ask_password = True
            password = password.encode()
            password_lenght = len(password)
            debug("Encrypt with your key.")
        else:
            ask_password = False
            password = choices(list(range(256)), k=40)
            password_lenght = 40
            debug("Encrypt with random key.")

        code = [
            char ^ password[i % password_lenght] for i, char in enumerate(code.encode())
        ]

        if ask_password:
            code = self.code = (
                "_=input('Password: ').encode();__=len(_);___=exec;_____='';"
                f"\nfor _______,______ in enumerate({code}):_____+=chr"
                "(______^_[_______%__])\n___(_____)"
            )
        else:
            code = self.code = (
                f"_={password};__=len(_);___=exec;_____='';\nfor _______,______ "
                f"in enumerate({code}):_____+=chr(______^_[_______%__])\n___(_____)"
            )

        debug("Code is encrypted with XOR.")
        return code

    def base85(self, code: str = None) -> str:
        """
        This function encodes python code with base85.
           (Level 5)

        - if code is None this function use self.code
        - self.code is set encoded code
        - returns the base85 encoded code

        >>> exec(Obfuscator("").base85("print('Hello World !')"))
        Hello World !
        >>>
        """

        code = code or self.code

        if self.level < 5:
            return code

        code = b85encode(code.encode())
        code = (
            self.code
        ) = f"from base64 import b85decode as _;___=bytes.decode;__=exec;__(___(_({code})))"
        debug("Code is encoded with base85")

        return code

    def delete_field(self, element: AST, field: str) -> AST:
        """
        This function deletes field in AST object.
        """

        dict_ = element.__dict__
        if field in dict_.keys():
            del dict_[field]
            element._fields = tuple(dict_.keys())
            info(f"Deleted {field} in {type(element)}")

        return element

    def delete_annotations(self, element: AST) -> AST:
        """
        This function deletes annotations in AST object.
        """

        return self.delete_field(element, "annotation")

    def delete_returns(self, element: AST) -> AST:
        """
        This function deletes returns in AST object.
        """

        return self.delete_field(element, "returns")

    def init_builtins(self) -> str:
        """
        This function obfuscates default variables and builtins names.
        """

        names = tuple(map(self.get_random_name, dir(builtins) + default_dir))

        default_variables = self.default_variables = (
            f"{','.join([name.obfuscation for name in names])}"
            f"={','.join([name.name for name in names])}\n"
        )
        info("Builtins obfuscated.")

        return default_variables

    def init_import(self, code: str = None) -> Tuple[str, AST]:
        """
        This function adds an import function to try module 'from <module>.<module> import <module>'.

        code(str) = None: if code this function use this code else it use self.code
        self.code is set to the new code
        Return the new code and AST.
        """

        code = code or self.code

        self.code = code = (
            (
                "def myimport(module, element):\n\ttry:return __import__(module+'.'+element)"
                "\n\texcept ImportError:return __import__(module)"
                f"\n{self.code}"
            )
            if code
            else (
                "def myimport(module, element):\n\ttry:return __import__(module+'.'+element)"
                "\n\texcept ImportError:return __import__(module)\n"
            )
        )

        astcode = self.astcode = parse(code)
        info("Import function is added to code.")
        return code, astcode

    def init_crypt_strings(self, code: str = None) -> Tuple[str, AST]:
        """
        This function adds the decrypt function to decrypt obfuscated/encrypted strings.

        code(str) = None: if code this function use this code else it use self.code
        self.code is set to the new code
        Return the new code and AST.
        """

        code = code or self.code
        self._xor_password_key = choices(
            list(range(256)), k=self._xor_password_key_length
        )

        if self.level < 2:
            return code, self.astcode

        self.code = code = (
            (
                "xor=lambda bytes_:(bytes([x^"
                f"{self._xor_password_key}[i%{self._xor_password_key_length}]"
                f" for i,x in enumerate(bytes_)]))\n{self.code}"
            )
            if code
            else (
                "xor=lambda bytes_:(bytes([x^"
                f"{self._xor_password_key}[i%{self._xor_password_key_length}]"
                " for i,x in enumerate(bytes_)]))\n"
            )
        )

        astcode = self.astcode = parse(code)
        info("Encrypt/decrypt (XOR) function is added to code.")
        return code, astcode

    def xor(self, data: bytes) -> bytes:
        """
        This function encrypts data.

        data(bytes): data to encrypt
        return encrypted bytes
        """

        if self._xor_password_key is None:
            raise RuntimeError("To encrypt data the encryption key must be set.")

        cipher = [
            byte ^ self._xor_password_key[i % self._xor_password_key_length]
            for i, byte in enumerate(data)
        ]
        return bytes(cipher)

    def set_namespace_name(self, name: str) -> str:
        """
        This function sets current namespace name.

        returns old namespace name

        >>> obfu = Obfuscator("")
        >>> obfu.set_namespace_name("Test")
        >>> obfu.set_namespace_name("test")
        'Test'
        >>> obfu.current_class
        'Test.test'
        >>>
        """

        namespace = self.current_class
        if namespace is not None:
            self.current_class += "." + name
        else:
            self.current_class = name

        return namespace

    def get_targets_and_value_for_import(
        self, module: str, elements: List[alias], is_from_import: bool = True
    ) -> Tuple[TupleAst, TupleAst]:
        """
        This function obfuscates 'from ... import ...'.
        """

        targets = []
        values = []

        for element in elements:
            alias = getattr(element, "asname", None) or element.name

            code = (
                None if "." not in module else f"myimport({module!r}, {element.name!r})"
            )
            for name in module.split(".")[1:]:
                code = f"getattr({code if code else module}, {name!r})"

            if is_from_import:
                code = f"""getattr({code if code else f'myimport({module!r}, {element.name!r})'}, {element.name!r})"""

            targets.append(NameAst(id=alias, ctx=Store()))
            values.append(parse(code).body[0].value)
            info(f"Obfuscates from {module!r} import {element.name!r}")

        # TODO add parse(start) to AST

        return TupleAst(elts=targets, ctx=Load()), TupleAst(elts=values, ctx=Load())

    @staticmethod
    def delete_doc_string(astcode: AST) -> AST:
        """
        This function deletes doc string in AST object.
        """

        for i, element in enumerate(astcode.body):
            if isinstance(element, Expr) and isinstance(element.value, Constant):
                del astcode.body[i]

        return astcode

    def string_obfuscation(self, string: str, no_backlash: bool = False) -> str:
        """
        This function obfuscate a string.
        """

        def to_hex(car: str) -> str:
            return f"'\\x{ord(car):0>2x}'"

        def to_octal(car: str) -> str:
            return f"'\\{ord(car):0>3o}'"

        def to_chr(car: str) -> str:
            return f"chr({ord(car)})"

        def to_chrbin(car: str) -> str:
            return f"chr({bin(ord(car))})"

        def to_chradd(car: str) -> str:
            value = ord(car)
            temp_value = randint(0, value)
            return f"chr({bin(temp_value)} + {oct(value - temp_value)})"

        def to_chrsub(car: str) -> str:
            value = ord(car)
            temp_value = randint(value, value * value)
            return f"chr({temp_value} - {temp_value - value})"

        if no_backlash:
            functions = (to_chr, to_chrbin, to_chradd, to_chrsub)
        else:
            functions = (
                to_hex,
                to_octal,
                to_chr,
                to_chrbin,
                to_chradd,
                to_chrsub,
            )
        string_repr = repr(string)
        code = self.code
        debug("Hard coded string obfuscation: " + string_repr)
        while string_repr in code:
            code = code.replace(
                string_repr,
                " + ".join(choice(functions)(car) for car in string),
                1,
            )
        self.code = code
        return code

    def int_call_obfuscation(self) -> str:
        """
        This method obfuscates int calls for int obfuscation.
        """

        code = self.code
        for match in finditer(r"\('0o[0-7]+', 8\)", code):
            string = match.group()
            debug("Int call obfuscation: " + repr(string))
            _8 = choice(
                (
                    'ord("\\x08")',
                    oct(8),
                    bin(8),
                    (lambda x: f"{x} - {x - 8}")(randint(8, 256 * 256)),
                )
            )
            value = string.split("'")[1]
            self.code = code.replace(string, f"('{value}', {_8})", 1)
            code = self.string_obfuscation(value)

        self.code = code
        return code

    def default_obfuscation(self) -> None:
        """
        This function starts the default obfuscation process.

        - get the code
        - initialize obfuscation
        - obfuscate names and values
        - obfuscate structure
        - save obfuscation, configuration and names to reverse obfuscation
        """

        self.using_default_obfu = True

        code, astcode = self.get_code()
        code, astcode = self.add_super_arguments(code)
        code, astcode = self.init_import(code)
        code, astcode = self.init_crypt_strings(code)
        self.init_builtins()
        astcode = self.visit(astcode)

        attributes_obfuscator = AttributeObfuscation(self)
        astcode = attributes_obfuscator.visit(astcode)

        self.code = unparse(astcode)

        for string in self.hard_coded_string:
            self.string_obfuscation(*string)
        self.code = self.int_call_obfuscation()

        code = self.add_builtins()
        code = self.gzip(code)
        code = self.xor_code(code)
        code = self.base85(code)
        self.code = self.hexadecimal(code)
        code = self.write_code()
        self.write_deobfuscate()

    def get_attributes_from(self, new_ast: AST, old_ast: AST) -> AST:
        """
        This function adds attributes from default AST to obfuscate AST.

        new_ast(AST): obfuscate AST without all attributes
        old_ast(AST): default AST with all attributes
        """

        new_ast_attr = dir(new_ast)

        for attribute in dir(old_ast):
            if attribute not in new_ast_attr:
                setattr(new_ast, attribute, getattr(old_ast, attribute))

        return new_ast

    def visit_ExceptHandler(self, astcode: ExceptHandler) -> ExceptHandler:
        """
        This function obfuscates the except syntax.
        """

        astcode = self.generic_visit(astcode)
        if astcode.name:
            astcode.name = self.get_random_name(astcode.name).obfuscation
            info("Added random name in except syntax.")
        return astcode

    def visit_JoinedStr(self, astcode: JoinedStr) -> JoinedStr:
        """
        This function changes the visit_Constant's behaviour.
        """

        debug("Enter in joined str...")
        self.in_format_string = True
        astcode = self.generic_visit(astcode)
        self.in_format_string = False
        debug("Joined str end.")
        return astcode

    def visit_Constant(self, astcode: Constant) -> Call:
        """
        This function encrypts python constants data.
           (Level 2)

        - self.astcode is set to obfuscate ast code
        - returns the obfuscate ast code
        """

        if self.level < 2:
            info("Level is less than 2 no Constant obfuscation.")
            return astcode

        is_str = isinstance(astcode.value, str)

        if is_str and not self.in_format_string:
            debug(f"String obfuscation for {astcode.value!r}.")
            astcode.value = astcode.value.encode(self.encoding)
            astcode = self.generic_visit(astcode)
            return Call(
                func=Call(
                    func=NameAst(
                        id=self.default_names["getattr"].obfuscation,
                        ctx=Load(),
                    ),
                    args=[
                        Call(
                            func=NameAst(
                                id=self.default_names["xor"].obfuscation,
                                ctx=Load(),
                            ),
                            args=[Constant(value=self.xor(astcode.value), kind=None)],
                            keywords=[],
                        ),
                        Constant(value="decode", kind=None),
                    ],
                    keywords=[],
                ),
                args=[Constant(value="utf-8", kind=None)],
                keywords=[],
            )

        elif isinstance(astcode.value, bytes):
            debug(f"Bytes obfuscation for {astcode.value!r}.")
            astcode = self.generic_visit(astcode)
            return Call(
                func=NameAst(id=self.default_names["xor"].obfuscation, ctx=Load()),
                args=[Constant(value=self.xor(astcode.value))],
                keywords=[],
            )

        elif isinstance(astcode.value, int) and not self.in_format_string:
            debug(f"Integer obfuscation for {astcode.value!r}")
            astcode = self.generic_visit(astcode)
            return Call(
                func=NameAst(id=self.default_names["int"].obfuscation, ctx=Load()),
                args=[
                    Constant(value=oct(astcode.value)),
                    Constant(value=8),
                ],
                keywords=[],
            )
        elif is_str:
            self.hard_coded_string.add((astcode.value, True))
        else:
            info(
                f"In format string {astcode.value!r} this constant type can't be obfuscated."
            )
            astcode = self.generic_visit(astcode)
        return astcode

    def visit_Module(self, astcode: Module) -> Module:
        """
        This function deletes the Module doc string.

        module(Module): module to obfuscate.
        if this module have doc string, doc string is delete.
        returns module.
        """

        if self.level >= 1:
            debug("Delete Module doc string.")
            astcode = self.delete_doc_string(astcode)
        else:
            info("Level is less than 1 no Module obfuscation.")

        astcode = self.generic_visit(astcode)
        return astcode

    def visit_ImportFrom(self, astcode: ImportFrom) -> Assign:
        """
        This function build a obfuscate 'from ... import ...'
        """

        if self.level < 1:
            info("Level is less than 1 no ImportFrom obfuscation.")
            astcode = self.generic_visit(astcode)
            return astcode

        if astcode.names[0].name == "*":
            module = __import__(astcode.module)

            for submodule in astcode.module.split(".")[1:]:
                module = getattr(module, submodule)

            astcode.names = [
                alias(name=name)
                for name in getattr(module, "__all__", dir(module))
                if not (
                    name.startswith("__")
                    and name.endswith("__")
                    and name in self.default_names.keys()
                )
                and name != "__path__"
            ]

        targets, values = self.get_targets_and_value_for_import(
            astcode.module, astcode.names
        )

        debug(f"'from {astcode.module} import' obfuscation.")
        assign = Assign(targets=[targets], value=values)
        astcode = self.get_attributes_from(assign, astcode)

        astcode = self.generic_visit(astcode)
        return astcode

    def visit_Import(self, astcode: Import) -> Assign:
        """
        This function obfuscates 'import ...'
        """

        if self.level < 1:
            info("Level is less than 1 no ImportFrom obfuscation.")
            astcode = self.generic_visit(astcode)
            return astcode

        modules = {
            alias.name: ModuleImport(
                alias.name.split(".")[0], alias.__dict__.get("asname")
            )
            for alias in astcode.names
        }
        debug(f"Import obfuscation ({', '.join(modules.keys())}).")

        targets = []
        values = []

        assign = Assign(
            targets=[TupleAst(elts=targets, ctx=Store())],
            value=TupleAst(elts=values, ctx=Load()),
        )

        for name, module in modules.items():
            if module.alias is None or "." not in name:
                values.append(
                    Call(
                        func=NameAst(id="__import__", ctx=Load()),
                        args=[Constant(value=name)],
                        keywords=[],
                    )
                )
            else:
                _, value = self.get_targets_and_value_for_import(
                    name,
                    [ElementImport(name.split(".")[-1], module.alias)],
                    False,
                )
                values.append(value.elts[0])

            targets.append(NameAst(id=module.alias or module.name, ctx=Store()))

        astcode = self.get_attributes_from(assign, astcode)
        astcode = self.generic_visit(astcode)
        return astcode

    def visit_ClassDef(self, astcode: ClassDef) -> ClassDef:
        """
        This function obfuscates the class name and delete the doc string.

        astcode(ClassDef): the class to obfuscate
        returns a ClassDef with different name without doc string
        """

        precedent_class = self.set_namespace_name(astcode.name)

        if self.level >= 1:
            debug(f"{astcode.name!r} (class definition) obfuscation.")
            astcode.name = self.get_random_name(astcode.name, True).obfuscation
            astcode = self.delete_doc_string(astcode)

        astcode = self.generic_visit(astcode)
        self.current_class = precedent_class
        return astcode

    def visit_AsyncFunctionDef(self, astcode: AsyncFunctionDef) -> AsyncFunctionDef:
        """
        This methods obfuscates asynchronous function
        using the function obfusction.

        astcode(AsyncFunctionDef): asynchronous function to obfuscate
        returns a AsyncFunctionDef with different name
        """

        return self.visit_FunctionDef(astcode)

    def visit_FunctionDef(self, astcode: FunctionDef) -> FunctionDef:
        """
        This function obfuscates function name if isn't a magic method.

        astcode(FunctionDef): function to obfuscate
        returns a FunctionDef with different name
        """

        precedent_class = self.set_namespace_name(astcode.name)

        if self.level >= 1:
            name = astcode.name
            if not (name.startswith("__") and name.endswith("__")):
                astcode.name = self.get_random_name(name, True).obfuscation
            debug(f"{astcode.name!r} function obfuscation.")
            astcode = self.delete_doc_string(astcode)

        astcode = self.generic_visit(astcode)
        self.current_class = precedent_class
        return astcode

    def visit_Name(self, astcode: NameAst) -> NameAst:
        """
        This function obfuscates name.

        astcode(Name): the name to obfuscate
        returns a Name with different id
        """

        if self.level >= 1:
            debug(f"Name obfuscation for {astcode.id!r}")
            astcode.id = self.get_random_name(astcode.id).obfuscation

        astcode = self.generic_visit(astcode)
        return astcode

    def visit_Global(self, astcode: Global) -> Global:
        """
        This function obfuscates global names

        astcode(Global): AST object to obfuscate
        returns a Global with different names
        """

        if self.level >= 1:
            for i, name in enumerate(astcode.names):
                astcode.names[i] = self.get_random_name(name).obfuscation
                debug(f"[Global] {name!r} obfuscation")

        astcode = self.generic_visit(astcode)
        return astcode

    def visit_arg(self, astcode: arg) -> arg:
        """
        This function obfuscates AST arg

        astcode(arg): the arg to obfuscate
        returns a AST arg with different arg name
        """

        if self.level >= 1:
            debug(f"arg obfuscation for {astcode.arg}")
            self.delete_field(astcode, "annotation")
            astcode.arg = self.get_random_name(astcode.arg).obfuscation

        astcode = self.generic_visit(astcode)
        return astcode

    def visit_AnnAssign(self, astcode: AnnAssign) -> Assign:
        """
        This function obfuscates assignation.

        astcode(AnnAssign): assign with annotation
        return an Assign obfuscated
        """

        if self.level >= 1:
            if isinstance(astcode.annotation, Name):
                debug(f"Delete annotation {astcode.annotation.id} from Assign")
            elif isinstance(astcode.annotation, Call):
                debug(f"Delete annotation {astcode.annotation.func.id} from Assign")
            else:
                debug(f"Delete unknown type annotation")

            assign = Assign(
                targets=[astcode.target],
                value=astcode.value if astcode.value else Constant(value=None),
            )
            astcode = self.get_attributes_from(assign, astcode)

        astcode = self.generic_visit(astcode)
        return astcode

    def write_deobfuscate(self) -> None:
        """
        This function saves configuration and the mapping between
        variable names and obfuscation names.
        """

        if not self.deobfuscate:
            return None

        config = {
            "Obfuscator": {
                "level": self.level,
                "encoding": self.encoding,
                "output_file": self.output_filename,
                "default_obfuscation": self.using_default_obfu,
            },
            "encryption_key": self.password,
            "names": [
                {
                    "name": name.name,
                    "definition": name.is_defined,
                    "namespace": name.namespace_name,
                    "obfuscation_name": name.obfuscation,
                }
                for name in self.default_names.values()
            ],
        }

        with open("deobfuscate.json", "w", encoding=self.encoding) as file:
            dump(config, file)

        debug("Writing file deobfuscate.txt")


class AttributeObfuscation(NodeTransformer):

    """
    This class obfuscates attribute name.
    """

    def __init__(self, obfuscator: Obfuscator):
        self.default_names = obfuscator.default_names
        self.obfu_names = obfuscator.obfu_names
        self.obfuscator = obfuscator
        self.in_assign = False

    def visit_Assign(self, assign: Assign) -> Assign:
        """
        This function defines attribute obfuscation mode.

        assign: Assign object
        return an Assign object with obfuscation
        """

        self.in_assign = True
        assign = self.generic_visit(assign)
        self.in_assign = False
        return assign

    def visit_AugAssign(self, assign: AugAssign) -> AugAssign:
        """
        This function defines attribute obfuscation mode.

        assign: AugAssign object
        return an AugAssign object with obfuscation
        """

        self.in_assign = True
        assign = self.generic_visit(assign)
        self.in_assign = False
        return assign

    def visit_JoinedStr(self, astcode: JoinedStr) -> JoinedStr:
        """
        This function changes the visit_Constant's behaviour.
        """

        self.obfuscator.in_format_string = True
        astcode = self.generic_visit(astcode)
        self.obfuscator.in_format_string = False
        return astcode

    def visit_Attribute(self, attribute: Attribute) -> Attribute:
        """
        This function obfuscate attribute name.

        attribute: Attribute object
        return an Attribute object with obfuscate name
        """

        if (name := self.default_names.get(attribute.attr)) is not None:
            debug(f"Change attribute: {attribute.attr}")
            if name.is_defined:
                attribute.attr = name.obfuscation

        if self.in_assign:
            return attribute

        constant = Constant(value=attribute.attr, kind=None)

        if attribute.attr != "decode":
            constant = self.obfuscator.visit_Constant(constant)

        return Call(
            func=NameAst(id=self.default_names["getattr"].obfuscation, ctx=Load()),
            args=[attribute.value, constant],
            keywords=[],
        )


def parse_args() -> Namespace:
    """
    This function parses command line arguments.
    """

    parser = ArgumentParser(description="This tool obfuscates python code.")
    add_argument = parser.add_argument

    add_argument("filename")
    add_argument(
        "--output-filename",
        "--output",
        "-o",
        default=None,
        help="Filename to write the obfuscate code.",
    )
    add_argument("--level", "-l", type=int, default=6, help="Obfuscation level to use.")
    add_argument(
        "--names",
        "-n",
        action="extend",
        nargs="+",
        help="Pre-defined names to uses (syntax: name:obfu_name).",
    )
    add_argument(
        "--deobfuscate",
        "-d",
        action="store_true",
        help="Save configuration and the mapping between obfuscation and default name.",
    )
    add_argument(
        "--password",
        "-w",
        default=None,
        help="Encryption key to encrypt the code.",
    )
    add_argument(
        "--file-encoding",
        "-e",
        default="utf-8",
        help="Encoding to open python file.",
    )
    add_argument(
        "--names-size",
        "-s",
        default=12,
        type=int,
        help="Obfuscation name size.",
    )
    add_argument(
        "--print",
        "-p",
        action="store_true",
        help="Print the obfuscate code in console.",
    )
    add_argument("--log-level", "-g", type=int, default=40, help="Log level.")
    add_argument("--log-filename", "-f", default=None, help="Log filename.")

    return parser.parse_args()


def main() -> int:
    """
    This function starts this tool from command line.
    """

    args = parse_args()

    names = {}

    if args.names is not None:
        for name in args.names:
            name, obfu_name = name.split(":", 1)
            names[name] = Name(name, obfu_name, False, None)

    basicConfig(
        filename=args.log_filename,
        level=args.log_level,
        format="%(levelname)s - %(message)s",
    )

    obfu = Obfuscator(
        args.filename,
        args.output_filename,
        args.level,
        names,
        args.deobfuscate,
        args.password,
        args.file_encoding,
        args.names_size,
    )
    obfu.default_obfuscation()

    if args.print:
        print(obfu.code)

    return 0


if __name__ == "__main__":
    exit(main())
