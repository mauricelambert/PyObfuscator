#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    This file implement a python code Obfuscator.
#    Copyright (C) 2021  Maurice Lambert

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

"""This file implement a python code Obfuscator.

>>> with open("code.py", "w") as f: n = f.write("print('Hello world !')")
>>> Obfuscator("code.py", deobfuscate_file=False).default_obfuscation()
>>> with open("code_obfu.py") as f: exec(f.read())
Hello world !
>>> from os import remove; remove("code.py"); remove("code_obfu.py")

To run some simples tests use: 
    - python3 -m doctest -v Obfuscator.py

To run all tests use:
    - ./test/Test_Obfuscator.py
    - python3 test/Test_Obfuscator.py -v # with verbose mode
    - python3 -m unittest -v test/Test_Obfuscator.py # using unittest module command (verbose mode)
    - cd test; python3 -m unittest discover # using unittest module and discover mode
"""

default_dir = dir()

from argparse import ArgumentParser, Namespace
from ast import unparse, AST, NodeTransformer
from typing import Tuple, Dict, List
from dataclasses import dataclass
from base64 import b85encode
from gzip import compress
from os import path
import builtins
import logging
import random
import string
import json
import ast


__all__ = [
    "Obfuscator",
    "ChangeAttributes",
    "main",
    "Name",
    "ObfuscationError",
    "DocPassword",
    "DocLevels",
]


class ObfuscationError(Exception):

    """This class is used to raise an ObfuscationError.

    >>> raise ObfuscationError("Obfuscation test error")
    Traceback (most recent call last):
       ...
    Obfuscator.ObfuscationError: Obfuscation test error
    """

    pass


class DocPassword:

    """Password is a string to encrypt python code with xor.

    if password is None:
        - random password is define and write in python file
        code is independent but it's easy to reverse this obfuscation
    if password is a string:
        - password is not written in python file, to run
        the code you must enter the password (console mode)

    Note: this password is not use if you don't use
    Obfuscator.xor_code function or Level is less than 4.
    """

    def print_the_doc():
        print(DocPassword.__doc__)


class DocLevels:

    """Level is an integer to define obfuscation level.

    if level equal 1:
        - variable name change (using Obfuscator.change_variables_name function)
            variables is less understandable
        - doc and signature is deleted
            function, class
    if level equal 2:
        - level 1
        - strings are encrypted (using Obfuscator.crypt_strings function)
            the strings become illegible but longer code execution
    if level equal 3:
        - level 2
        - gzip the code (using Obfuscator.gzip_encode function)
            the code structure becomes invisible but longer code execution
    if level equal 4:
        - level 3
        - xor (using Obfuscator.xor_code function)
            encrypt the code but longer code execution
    if level equal 5:
        - level 4
        - base85 (using Obfuscator.base85_encode function)
            bigger file size and longer code execution
    if level equal 6:
        - level 5
        - "hexa code" ('a' become '\\x061') (using Obfuscator.hexa_encode function)
            file size * 4
    """

    def print_the_doc():
        print(DocLevels.__doc__)


@dataclass
class Name:

    """Dataclass with default name, obfu name, definition and namespace.

    name(str): default variable name
    obfu_name(str): variable name obfuscation (a random name)
    is_defined(bool): a boolean representing the definition in file
    namespace_name(str): the namespace (None or <class name> or <class name>.<function name>)
    """

    name: str
    obfu_name: str
    is_defined: bool
    namespace_name: str


class ChangeAttributes(NodeTransformer):

    """This class change attribute if is defined in code."""

    def __init__(self, default_names: Dict[str, Name], obfu_names: Dict[str, Name]):
        self.default_names = default_names
        self.obfu_names = obfu_names

    def visit_Attribute(self, parsed_code: ast.Attribute) -> ast.Attribute:

        """This function change attribute name if attribute is defined.

        parsed_code: ast.Attribute object
        return an ast.Attribute object with the same name or with her obfuscate name
        """

        if (name := self.default_names.get(parsed_code.attr)) is not None:
            logging.debug(f"Change attribute: {parsed_code.attr}")
            if name.is_defined:
                parsed_code.attr = name.obfu_name

        return parsed_code


class Obfuscator(NodeTransformer):

    """This class obfuscate python file.

    filename(str): is the name of python file to obscate
    output_filename(str) = None: is the name of obfuscate python file
    level(int) = 5: is the obfuscation level (see the DocLevels's doc string for more information)
    names(Dict[str, Name]) = {}: pre-defined name (for example to import class or method in other file you need to know the name)
        For exemple: to import class named 'Obfuscator' as 'Fdg6jsT_2', names must be
        "{'Obfuscator': Name('Obfuscator', 'Fdg6jsT_2', False, None)}".
    deobfuscate_file(bool) = True: if True write old variable name and new variable name in json file to reverse obfuscation
    password(str) = None: password for xor encrypt (see the DocPassword's doc string for more information)
    file_encoding(str) = utf-8: python file enconding
    names_size(int) = 12: size to generate random variables names"""

    def __init__(
        self,
        filename: str,
        output_filename: str = None,
        level: int = 6,
        names: Dict[str, Name] = {},
        deobfuscate_file: bool = True,
        password: str = None,
        file_encoding: str = "utf-8",
        names_size: int = 12,
    ):
        self.filename = filename
        self.output_filename = (
            output_filename
            if output_filename
            else f"{path.splitext(filename)[0]}_obfu.py"
        )
        self.level = level
        self.deobfuscate_file = deobfuscate_file

        self.password = password
        self.code = None
        self.parsed_code = None

        self.default_names = names
        self.obfu_names = {v.obfu_name: v for v in names.values()}

        self.names_size = names_size
        self.encoding = file_encoding

        self._xor_password_key = None
        self._xor_password_key_length = 40
        self._dir_definition = None

        self.current_class = None
        self.default_is_define = False

        self.using_default_obfu = False

        super().__init__()

    def get_random_name(self, first_name: str, is_defined: bool = False) -> Name:

        """This function return a random variable name.

        >>> Obfuscator("").get_random_name("test").name
        'test'
        """

        if (name := self.default_names.get(first_name)) is not None:
            return name

        while name is None or name in self.obfu_names.keys():

            first = random.choice("_" + string.ascii_letters)
            name = "".join(
                random.choices(
                    "_" + string.ascii_letters + string.digits, k=self.names_size - 1
                )
            )

            name = first + name

        name = Name(
            first_name, name, is_defined or self.default_is_define, self.current_class
        )
        self.obfu_names[name.obfu_name] = name
        self.default_names[first_name] = name

        return name

    def get_code(self) -> Tuple[str, AST]:

        """This function return content and AST from python file."""

        with open(self.filename, encoding=self.encoding) as file:
            self.code = file.read()

        logging.debug(f"Get code from {self.filename}")

        self.parsed_code = ast.parse(self.code)
        return self.code, self.parsed_code

    def add_builtins(self) -> str:

        """This function add builtins obfuscation on the top of the file
        and return the new code (self.code is set wih the new code).

        This function raise ObfuscationError if builtins are not obfuscate.
        (Use Obfuscator.init_vars function to obfuscate builtins)

        This function raise ObfuscationError if self.code is None.
        """

        if self._dir_definition is None:
            raise ObfuscationError(
                "Builtins obfuscation is required"
                " to write the code. Use: Obfuscator.init_vars."
            )

        if self.code is None:
            raise ObfuscationError("self.code is required to write the code")

        self.code = f"{self._dir_definition}{self.code}"
        return self.code

    def write_code(self) -> Tuple[str, AST]:

        """This function write obfuscate code in output file,
        return an obfuscate code.

        This function raise ObfuscationError if self.code is None.
        """

        if self.code is None:
            raise ObfuscationError("self.code is required to write the code")

        with open(self.output_filename, "w", encoding=self.encoding) as file:
            file.write(self.code)

        logging.debug(f"Write obfuscate code in {self.output_filename}")

        return self.code

    def gzip_encode(self, code: str = None) -> str:

        """This function transform python code into gzip-ed python code.
           (Level 3)

        - if code is None this function use self.code
        - in this function self.code is set to gzip-ed python code
        - this function return the gzip-ed python code

        >>> exec(Obfuscator("").gzip_encode("print('Hello World !')"))
        Hello World !
        """

        self.code = code if code else self.code

        if self.level >= 3:
            self.code = compress(self.code.encode())
            self.code = f"from gzip import decompress as __;_=exec;_(__({self.code}))"

            logging.debug("Get gzipped code.")

        return self.code

    def hexa_encode(self, code: str = None) -> str:

        """This function transform python code into python hexa code ('a' become '\\x61').
           (Level 6)

        - if code is None this function use self.code
        - in this function self.code is set to hexa python code
        - this function return the hexa python code

        >>> exec(Obfuscator("").hexa_encode("print('Hello World !')"))
        Hello World !
        """

        self.code = code if code else self.code

        if self.level >= 6:
            self.code = "".join(
                [hex(ord(car)).replace("0x", "\\x") for car in self.code]
            )
            self.code = f"_=exec;_('{self.code}')"

            logging.debug("Get hexa code.")

        return self.code

    def xor_code(self, code: str = None, password: str = None) -> str:

        """This function transform python code into xor-ed python code.
           (Level 4)

        - if code is None this function use self.code
        - if password is None this function use self.password
               (see the DocPassword's doc string for more information)
        - if self.password is None this function generate a random password
               (see the DocPassword's doc string for more information)
        - in this function self.code is set to xor-ed python code
        - this function return the xor-ed python code

        >>> exec(Obfuscator("").xor_code("print('Hello World !')"))
        Hello World !
        """

        self.code = code if code else self.code
        self.password = password if password else self.password

        if self.password:
            ask_password = True
            password = [ord(x) for x in self.password]
            password_lenght = len(password)

            logging.debug("Using your XOR key.")
        else:
            ask_password = False
            password = random.choices(list(range(256)), k=40)
            password_lenght = 40

            logging.debug("Generate xor key.")

        if self.level >= 4:
            self.code = [
                ord(x) ^ password[i % password_lenght] for i, x in enumerate(self.code)
            ]

            if ask_password:
                self.code = (
                    "_=input('Password: ').encode();__=len(_);___=exec;_____='';"
                    f"\nfor _______,______ in enumerate({self.code}):_____+=chr"
                    "(______^_[_______%__])\n___(_____)"
                )
            else:
                self.code = (
                    f"_={password};__=len(_);___=exec;_____='';\nfor _______,______ "
                    f"in enumerate({self.code}):_____+=chr(______^_[_______%__])\n___(_____)"
                )

            logging.debug("Get XORed code.")

        return self.code

    def base85_encode(self, code: str = None) -> str:

        """This function transform python code into base85 python code.
           (Level 5)

        - if code is None this function use self.code
        - in this function self.code is set to base85 python code
        - this function return the base85 python code

        >>> exec(Obfuscator("").base85_encode("print('Hello World !')"))
        Hello World !
        """

        self.code = code if code else self.code

        if self.level >= 5:
            self.code = b85encode(self.code.encode())
            self.code = (
                f"from base64 import b85decode;exec(b85decode({self.code}).decode())"
            )

            logging.debug("Get base85 encoded code.")

        return self.code

    def delete_field(self, parsed_code: AST, field: str) -> AST:

        """This function delete field in AST object."""

        if field in parsed_code.__dict__.keys():
            del parsed_code.__dict__[field]
            parsed_code._fields = tuple(parsed_code.__dict__.keys())

            logging.info(f"Delete {field} in {type(parsed_code)}")

        return parsed_code

    def delete_annotations(self, parsed_code: AST) -> AST:

        """This function delete annotations in AST object."""

        return self.delete_field(parsed_code, "annotation")

    def delete_returns(self, parsed_code: AST) -> AST:

        """This function delete returns in AST object."""

        return self.delete_field(parsed_code, "returns")

    def init_vars(self) -> str:

        """This function obfuscate default names like __builtins__ and
        other default names.

        Return constant definition code.
        """

        global default_dir

        names = [self.get_random_name(name) for name in dir(builtins) + default_dir]

        self._dir_definition = (
            f"{','.join([name.obfu_name for name in names])}"
            f"={','.join([name.name for name in names])}\n"
        )
        logging.info("Default vars are obfuscated.")

        return self._dir_definition

    def init_crypt_strings(self, code: str = None) -> str:

        """This function add to the code a xor lambda to encrypt strings.

        code(str) = None: if code this function use this code else it use self.code
        self.code is set to the new code
        Return the new code.
        """

        self._xor_password_key = random.choices(
            list(range(256)), k=self._xor_password_key_length
        )

        if code:
            self.code = code

        if self.level >= 2:
            if self.code:
                self.code = (
                    "xor=lambda bytes_:(bytes([x^"
                    f"{self._xor_password_key}[i%{self._xor_password_key_length}]"
                    f" for i,x in enumerate(bytes_)]))\n{self.code}"
                )
            else:
                self.code = (
                    "xor=lambda bytes_:(bytes([x^"
                    f"{self._xor_password_key}[i%{self._xor_password_key_length}]"
                    " for i,x in enumerate(bytes_)]))\n"
                )

            self.parsed_code = ast.parse(self.code)
            logging.info("XOR function is build to obfuscate strings.")

        return self.code

    def xor(self, data: bytes) -> bytes:

        """This function encrypt data (string or bytes).

        data(bytes): data to encrypt
        return encrypted bytes
        """

        if self._xor_password_key is None:
            raise ObfuscationError(
                "to use Obfuscator.xor function init Obfuscator._xor_password_key"
                " using Obfuscator.init_crypt_strings"
            )

        cipher = []
        for i, byte in enumerate(data):
            cipher.append(
                byte ^ self._xor_password_key[i % self._xor_password_key_length]
            )
        return bytes(cipher)

    def set_current_name(self, name: str) -> str:

        """This function set current name of namespace.

        return old current name

        >>> obfu = Obfuscator("")
        >>> obfu.set_current_name("Test")
        >>> obfu.set_current_name("test")
        'Test'
        >>> obfu.current_class
        'Test.test'
        """

        precedent_class = self.current_class
        if precedent_class is not None:
            self.current_class += "." + name
        else:
            self.current_class = name

        return precedent_class

    def get_targets_and_value_from_import_from(
        self, module: str, elements: List[ast.alias]
    ) -> Tuple[ast.Tuple, ast.Tuple]:

        """This function build Tuples for a custom "from ... import ..." """

        targets = []
        values = []

        for element in elements:
            alias = element.__dict__.get("asname") or element.name

            targets.append(ast.Name(id=alias, ctx=ast.Store()))
            values.append(
                ast.Subscript(
                    value=ast.Attribute(
                        value=ast.Call(
                            func=ast.Name(id="__import__", ctx=ast.Load()),
                            args=[ast.Constant(value=module)],
                            keywords=[],
                        ),
                        attr="__dict__",
                        ctx=ast.Load(),
                    ),
                    slice=ast.Constant(value=element.name),
                    ctx=ast.Load(),
                )
            )

        logging.info(f"Build import for {module}.{element.name}")

        return ast.Tuple(elts=targets, ctx=ast.Load()), ast.Tuple(
            elts=values, ctx=ast.Load()
        )

    def delete_doc_string(self, parsed_code: AST) -> AST:

        """This function delete doc string in AST object."""

        for i, element in enumerate(parsed_code.body):
            if isinstance(element, ast.Expr) and isinstance(
                element.value, ast.Constant
            ):
                del parsed_code.body[i]

        return parsed_code

    def default_obfuscation(self) -> None:

        """This function launch the default obfuscation.

        - get the code
        - initialize obfuscation
        - change code (variables names, string)
        - change structure (stringify and obfuscate this string)
        - write code and save names (random names + default names)
        """

        self.using_default_obfu = True

        code, parsed_code = self.get_code()
        code = self.init_crypt_strings()
        obfu_default_vars = self.init_vars()
        parsed_code = self.visit(self.parsed_code)

        change_attr = ChangeAttributes(self.default_names, self.obfu_names)
        self.parsed_code = change_attr.visit(self.parsed_code)

        self.code = unparse(self.parsed_code)
        obfu_code = self.add_builtins()
        obfu_code = self.gzip_encode()
        obfu_code = self.xor_code()
        obfu_code = self.base85_encode()
        obfu_code = self.hexa_encode()
        obfu_code = self.write_code()
        self.write_deobfuscate()

    def get_attributes_from(self, new_ast: AST, old_ast: AST) -> AST:

        """This function add attribute for new AST object from
        default AST object.

        new_ast(AST): new AST without all attributes
        old_ast(AST): default AST with all attributes
        """

        new_ast_attr = dir(new_ast)

        for attribute in dir(old_ast):
            if attribute not in new_ast_attr:
                setattr(new_ast, attribute, getattr(old_ast, attribute))

        return new_ast

    def visit_Constant(self, parsed_code: ast.Constant = None) -> ast.Call:

        """This function crypt strings/bytes of python code.
           (Level 2)

        - if parsed_code is None this function use self.parsed_code
        - in this function self.parsed_code is set to the new parsed python code
        - this function return the new parsed python code
        """

        if self.level >= 2:
            if isinstance(parsed_code.value, str):
                logging.debug(f"Str Constant obfuscation for {parsed_code.value}.")
                parsed_code.value = parsed_code.value.encode(self.encoding)
                self.generic_visit(parsed_code)

                return ast.Call(
                    func=ast.Attribute(
                        value=ast.Call(
                            func=ast.Name(
                                id=self.default_names["xor"].obfu_name, ctx=ast.Load()
                            ),
                            args=[ast.Constant(value=self.xor(parsed_code.value))],
                            keywords=[],
                        ),
                        attr="decode",
                        ctx=ast.Load(),
                    ),
                    args=[ast.Constant(value=self.encoding)],
                    keywords=[],
                )

            elif not isinstance(parsed_code.value, bytes):

                logging.info("Constant isn't str, this Constant can't be obfuscate.")
                self.generic_visit(parsed_code)
                return parsed_code
            elif isinstance(parsed_code.value, bytes):

                logging.debug("Bytes Constant obfuscation.")
                self.generic_visit(parsed_code)
                return ast.Call(
                    func=ast.Name(
                        id=self.default_names["xor"].obfu_name, ctx=ast.Load()
                    ),
                    args=[ast.Constant(value=self.xor(parsed_code.value))],
                    keywords=[],
                )
        else:

            logging.info("Level is less than 2 no Constant obfuscation.")
            return parsed_code

    def visit_Module(self, parsed_code: ast.Module) -> ast.Module:

        """This function delete doc of ast.Module.

        module(ast.Module): is the module.
        if this module have doc string, doc string is delete.
        return module.
        """

        if self.level >= 1:
            logging.debug("Delete Module doc string.")
            parsed_code = self.delete_doc_string(parsed_code)
        else:
            logging.info("Level is less than 1 no Module obfuscation.")

        self.generic_visit(parsed_code)
        return parsed_code

    def visit_ImportFrom(self, parsed_code: ast.ImportFrom) -> ast.Assign:

        """This function build a obfuscate "from ... import ..." """

        if self.level >= 1:

            if parsed_code.names[0].name == "*":
                module = __import__(parsed_code.module)
                parsed_code.names = [
                    ast.alias(name=name)
                    for name in dir(module)
                    if not (
                        name.startswith("__")
                        and name.endswith("__")
                        and name in self.default_names.keys()
                    )
                ]

            targets, values = self.get_targets_and_value_from_import_from(
                parsed_code.module, parsed_code.names
            )

            logging.debug(f"ImportFrom obfuscation of {parsed_code.module}.")
            assign = ast.Assign(targets=[targets], value=values)
            parsed_code = self.get_attributes_from(assign, parsed_code)

        else:
            logging.info("Level is less than 1 no ImportFrom obfuscation.")

        self.generic_visit(parsed_code)
        return parsed_code

    def visit_Import(self, parsed_code: ast.Import) -> ast.Assign:

        """This function build a obfuscate "import ..." """

        if self.level >= 1:
            modules = {
                alias.name: alias.__dict__.get("asname") or alias.name
                for alias in parsed_code.names
            }
            logging.debug(f"Import obfuscation of {', '.join(modules.keys())}.")

            assign = ast.Assign(
                targets=[ast.Tuple(elts=[], ctx=ast.Store())],
                value=ast.Tuple(elts=[], ctx=ast.Load()),
            )

            for module, name in modules.items():

                assign.targets[0].elts.append(ast.Name(id=name, ctx=ast.Store()))
                assign.value.elts.append(
                    ast.Call(
                        func=ast.Name(id="__import__", ctx=ast.Load()),
                        args=[ast.Constant(value=module)],
                        keywords=[],
                    )
                )

            parsed_code = self.get_attributes_from(assign, parsed_code)
        else:
            logging.info("Level is less than 1 no ImportFrom obfuscation.")

        self.generic_visit(parsed_code)
        return parsed_code

    def visit_ClassDef(self, parsed_code: ast.ClassDef) -> ast.ClassDef:

        """This function change ClassDef.name and delete doc string

        parsed_code(ClassDef): the ClassDef
        return same ClassDef with different name
        """

        precedent_class = self.set_current_name(parsed_code.name)

        if self.level >= 1:
            logging.debug(f"ClassDef Obfuscation for {parsed_code.name}.")
            parsed_code.name = self.get_random_name(parsed_code.name, True).obfu_name
            parsed_code = self.delete_doc_string(parsed_code)

        self.generic_visit(parsed_code)
        self.current_class = precedent_class
        return parsed_code

    def visit_FunctionDef(self, parsed_code: ast.FunctionDef) -> ast.FunctionDef:

        """This function change FunctionDef.name if don't start and end with "__".

        parsed_code(FunctionDef): the FunctionDef
        return same FunctionDef with different name
        """

        precedent_class = self.set_current_name(parsed_code.name)

        if self.level >= 1:
            if not (
                parsed_code.name.startswith("__") and parsed_code.name.endswith("__")
            ):
                parsed_code.name = self.get_random_name(
                    parsed_code.name, True
                ).obfu_name
            logging.debug(f"FunctionDef Obfuscation for {parsed_code.name}.")
            parsed_code = self.delete_doc_string(parsed_code)

        self.generic_visit(parsed_code)
        self.current_class = precedent_class
        return parsed_code

    def visit_Name(self, parsed_code: ast.Name) -> ast.Name:

        """This function change Name.id

        parsed_code(Name): the Name
        return same Name with different id
        """

        if self.level >= 1:
            logging.debug(f"Name obfuscation for {parsed_code.id}")
            parsed_code.id = self.get_random_name(parsed_code.id).obfu_name

        self.generic_visit(parsed_code)
        return parsed_code

    def visit_Global(self, parsed_code: ast.Global) -> ast.Global:

        """This function change Global.names

        parsed_code(Global): the Global
        return same Global with different names
        """

        if self.level >= 1:
            for i, name in enumerate(parsed_code.names):
                parsed_code.names[i] = self.get_random_name(name).obfu_name
                logging.debug(f"[Global] obfuscation, name: {name}")

        self.generic_visit(parsed_code)
        return parsed_code

    def visit_arg(self, parsed_code: ast.arg) -> ast.arg:

        """This function change arg.arg

        parsed_code(arg): the arg
        return same arg with different arg
        """

        if self.level >= 1:
            logging.debug(f"arg obfuscation for {parsed_code.arg}")
            self.delete_field(parsed_code, "annotation")
            parsed_code.arg = self.get_random_name(parsed_code.arg).obfu_name

        self.generic_visit(parsed_code)
        return parsed_code

    def visit_AnnAssign(self, parsed_code: ast.AnnAssign) -> ast.Assign:

        """This function build a ast.Assign object from
        ast.AnnAssign objet to delete annotation.

        parsed_code(AnnAssign): assign with annotation
        return Assign
        """

        if self.level >= 1:
            logging.debug(f"Delete annotation {parsed_code.annotation.id} from assign")

            assign = ast.Assign(targets=[parsed_code.target], value=parsed_code.value)
            parsed_code = self.get_attributes_from(assign, parsed_code)

        self.generic_visit(parsed_code)
        return parsed_code

    def write_deobfuscate(self):

        """This function write a file with obfuscate and default names
        to reverse name obfuscation."""

        if self.deobfuscate_file:

            config = {
                "Obfuscator": {
                    "level": self.level,
                    "default_obfuscation": self.using_default_obfu,
                    "encoding": self.encoding,
                    "output_file": self.output_filename,
                },
                "xor_encrypt": {"key": self.password},
                "names": [
                    {
                        "name": name.name,
                        "obfuscation_name": name.obfu_name,
                        "definition": name.is_defined,
                        "namespace": name.namespace_name,
                    }
                    for name in self.default_names.values()
                ],
            }

            with open("deobfuscate.json", "w", encoding=self.encoding) as file:
                file.write(json.dumps(config, indent=4))

            logging.debug("Writing file deobfuscate.txt")


def parse() -> Namespace:

    """ Function to parse arguments. """

    parser = ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument(
        "--output-filename",
        "-o",
        default=None,
        help="Filename to write the obfuscate code.",
    )
    parser.add_argument(
        "--level", "-l", type=int, default=6, help="Obfuscation level to use."
    )
    parser.add_argument(
        "--names",
        "-n",
        action="extend",
        nargs="+",
        help="Pre-defined names to uses (syntax: name:obfu_name).",
    )
    parser.add_argument(
        "--deobfuscate-file",
        "-d",
        action="store_true",
        help="Write a file with obfusctae names and default name for reversing.",
    )
    parser.add_argument(
        "--password",
        "-w",
        default=None,
        help="Password to use to encrypt the obfuscate code.",
    )
    parser.add_argument(
        "--file-encoding", "-e", default="utf-8", help="Encoding to open python file."
    )
    parser.add_argument(
        "--names-size", "-s", default=12, type=int, help="Obfuscation name size."
    )
    parser.add_argument(
        "--print",
        "-p",
        action="store_true",
        help="Print the obfuscate code in console.",
    )
    parser.add_argument("--log-level", "-g", type=int, default=40, help="Log level.")
    parser.add_argument("--log-filename", "-f", default=None, help="Log filename.")
    return parser.parse_args()


def main() -> None:

    """Command line main function to launch
    Obfuscation from your terminal."""

    args = parse()

    names = {}

    if args.names is not None:
        for name in args.names:
            name, obfu_name = name.split(":", 1)
            names[name] = Name(name, obfu_name, False, None)

    logging.basicConfig(
        filename=args.log_filename,
        level=args.log_level,
        format="%(levelname)s - %(message)s",
    )

    obfu = Obfuscator(
        args.filename,
        args.output_filename,
        args.level,
        names,
        args.deobfuscate_file,
        args.password,
        args.file_encoding,
        args.names_size,
    )
    obfu.default_obfuscation()

    if args.print:
        print(obfu.code)


if __name__ == "__main__":
    main()
