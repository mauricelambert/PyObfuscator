#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    Test for file named Obfuscator.py
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

""" Commands to launch tests:
    - ./Test_Obfuscator.py # if is executable file without verbose mode
    - python3 Test_Obfuscator.py -v # with verbose mode
    - python3 -m unittest -v Test_Obfuscator.py # using unittest module command (verbose mode)
    - python3 -m unittest discover # using unittest module and discover mode

Some times Test_Obfuscator.test_gzip_encode failed because gziped bytes break the regex test.
"""

default_dir = dir()

from os import path, getcwd, remove, environ
from unittest.mock import MagicMock, Mock
from unittest import TestCase
import unittest
import json
import ast
import sys

sys.path.append(path.join(path.dirname(__file__), "..", "PyObfuscator"))

from Obfuscator import Obfuscator, ObfuscationError, Name, ChangeAttributes


class Test_Name(TestCase):
    def test_build_Name(self):
        name = Name("name", "obfu_name", False, None)
        self.assertIsInstance(name, Name, "a Name is not instance of Name")
        self.assertIsNone(
            name.namespace_name,
            "When Name.namespace_name is defined as None, isn't None",
        )
        self.assertFalse(
            name.is_defined, "When Name.is_defined is defined as False, isn't False"
        )
        self.assertEqual(
            name.name,
            "name",
            "When Name.name is defined as 'name', isn't equal to 'name'",
        )
        self.assertEqual(
            name.obfu_name,
            "obfu_name",
            "When Name.obfu_name is defined as 'obfu_name', isn't equal to 'obfu_name'",
        )


class Test_ObfuscationError(TestCase):
    def test_raise(self):
        with self.assertRaises(
            ObfuscationError, msg="raise ObfuscationError don't raise ObfuscationError."
        ):
            raise ObfuscationError("Test ObfuscationError.")


class Test_ChangeAttributes(TestCase):
    def test_visit_Attribute(self):
        name1 = Name("test1", "obfu1", True, None)
        name2 = Name("test2", "obfu2", False, None)
        default = {"test1": name1, "test2": name2}
        obfu = {"obfu1": name1, "obfu2": name2}

        attribute1 = ast.Attribute(
            value=ast.Name(id="self", ctx=ast.Load()), attr="test1", ctx=ast.Load()
        )
        attribute2 = ast.Attribute(
            value=ast.Name(id="self", ctx=ast.Load()), attr="test2", ctx=ast.Load()
        )
        obfu = ChangeAttributes(default, obfu)

        attribute1 = obfu.visit(attribute1)
        attribute2 = obfu.visit(attribute2)

        self.assertEqual(
            attribute2.attr, "test2", "visit_Attribute change undefined name"
        )
        self.assertEqual(
            attribute1.attr, "obfu1", "visit_Attribute don't change defined name"
        )


class Test_Obfuscator(TestCase):
    def test_set_current_name(self):
        obfu = Obfuscator("")

        self.assertIsNone(
            obfu.current_class, "default Obfuscator.current_name is not None"
        )
        precedent_name = obfu.set_current_name("abc")
        self.assertIsNone(
            precedent_name,
            "Obfuscator.set_current_name don't return the precedent name",
        )
        self.assertEqual(
            "abc",
            obfu.current_class,
            "Obfuscator.set_current_name don't set the good name",
        )
        precedent_name = obfu.set_current_name("test")
        self.assertEqual(
            precedent_name,
            "abc",
            "Obfuscator.set_current_name don't return the precedent name",
        )
        self.assertEqual(
            "abc.test",
            obfu.current_class,
            "Obfuscator.set_current_name don't set the good name",
        )

    def test_get_random_name(self):
        from string import ascii_letters

        obfu = Obfuscator("")
        name = obfu.get_random_name("abc")

        self.assertEqual(
            name,
            obfu.get_random_name("abc"),
            "get_random_name don't return initialised name",
        )

        self.assertIsInstance(name, Name, "get_rendom_name don't return a str")
        self.assertEqual(
            len(name.obfu_name), 12, "Default get_random_name length is not 12."
        )

        for i in range(100):
            name = obfu.get_random_name(name.obfu_name)
            self.assertIn(
                name.obfu_name[0],
                ascii_letters + "_",
                "First character of get_random_name isn't valid.",
            )
            self.assertRegex(
                name.obfu_name,
                "^[a-zA-Z_][a-zA-Z0-9_]{11}$",
                "Name returned by get_random_name is not valid.",
            )

    def test_get_code(self):
        from ast import AST, dump

        test_filename = path.join(getcwd(), "test.py")

        with open(test_filename, "w") as file:
            file.write("print('Hello World !')")

        obfu = Obfuscator(test_filename)
        code, parsed_code = obfu.get_code()

        self.assertIsInstance(
            code, str, "First returned value of get_code is not a str"
        )
        self.assertIsInstance(
            parsed_code, AST, "Second returned value of get_code is not a ast.AST"
        )

        self.assertEqual(
            code, "print('Hello World !')", "get_code don't return the good code"
        )

        self.assertIn(
            "Hello World !", dump(parsed_code), "get_code don't return the good ast.AST"
        )
        self.assertIn(
            "print", dump(parsed_code), "get_code don't return the good ast.AST"
        )

        remove(test_filename)

    def test_gzip_encode(self):
        mock = Mock()
        mock.level = 0

        mock.code = "environ['test'] = 'Hello World !'"
        code = "environ['test'] = 'Python Hello World !'"

        obfu = Obfuscator("")
        self.assertEqual(
            Obfuscator.gzip_encode(mock),
            "environ['test'] = 'Hello World !'",
            "gzip_encode change code with level 0",
        )

        mock.level = 6
        gziped_code = Obfuscator.gzip_encode(mock)

        #########################
        ##  TEST WITHOUT PARAMS
        #########################

        for zipped_code in (gziped_code, mock.code):
            self.assertRegex(
                zipped_code,
                "^from gzip import decompress as __;_=exec;_[(]__[(]b'.*'[)]{2}$",
                "gzip_encode don't return the good python code",
            )
            exec(zipped_code)

            self.assertEqual(
                environ["test"],
                "Hello World !",
                "gzip_encode don't execute the good python code",
            )

        #########################
        ##  TEST WITH PARAMS
        #########################

        gziped_code = obfu.gzip_encode(code)

        for zipped_code in (gziped_code, obfu.code):
            self.assertRegex(
                zipped_code,
                "^from gzip import decompress as __;_=exec;_[(]__[(]b'.*'[)]{2}$",
                "gzip_encode don't return the good python code",
            )
            exec(zipped_code)

            self.assertEqual(
                environ["test"],
                "Python Hello World !",
                "gzip_encode don't execute the good python code",
            )

    def test_hexa_encode(self):
        mock = Mock()
        mock.level = 0

        mock.code = "environ['test'] = 'Hello World !'"
        non_obfu_code1_length = len(mock.code)

        code = "environ['test'] = 'Python Hello World !'"
        non_obfu_code2_length = len(code)

        obfu = Obfuscator("")
        self.assertEqual(
            Obfuscator.hexa_encode(mock),
            "environ['test'] = 'Hello World !'",
            "hexa_encode change code with level 0",
        )

        mock.level = 6
        hexa_code = Obfuscator.hexa_encode(mock)

        #########################
        ##  TEST WITHOUT PARAMS
        #########################

        for hexa__code in (hexa_code, mock.code):
            self.assertRegex(
                hexa__code,
                r"^_=exec;_[(]'(\\x[0-9a-f]{2}){size}'[)]$".replace(
                    "size", str(non_obfu_code1_length)
                ),
                "hexa_encode don't return the good python code",
            )
            exec(hexa__code)

            self.assertEqual(
                environ["test"],
                "Hello World !",
                "hexa_encode don't execute the good python code",
            )

        #########################
        ##  TEST WITH PARAMS
        #########################

        hexa_code = obfu.hexa_encode(code)

        for hexa__code in (hexa_code, obfu.code):
            self.assertRegex(
                hexa__code,
                r"^_=exec;_[(]'(\\x[0-9a-f]{2}){size}'[)]$".replace(
                    "size", str(non_obfu_code2_length)
                ),
                "hexa_encode don't return the good python code",
            )
            exec(hexa__code)

            self.assertEqual(
                environ["test"],
                "Python Hello World !",
                "hexa_encode don't execute the good python code",
            )

    def test_base85_encode(self):
        mock = Mock()
        mock.level = 0

        mock.code = "environ['test'] = 'Hello World !'"
        code = "environ['test'] = 'Python Hello World !'"

        obfu = Obfuscator("")
        self.assertEqual(
            Obfuscator.hexa_encode(mock),
            "environ['test'] = 'Hello World !'",
            "base85_encode change code with level 0",
        )

        mock.level = 6
        base85_code = Obfuscator.base85_encode(mock)

        #########################
        ##  TEST WITHOUT PARAMS
        #########################

        for encoded_code in (base85_code, mock.code):
            self.assertRegex(
                encoded_code,
                "^from base64 import b85decode;exec[(]b85decode[(]b'.*'[)].decode[(][)]{2}$",
                "base85_encode don't return the good python code",
            )
            exec(encoded_code)

            self.assertEqual(
                environ["test"],
                "Hello World !",
                "base85_encode don't execute the good python code",
            )

        #########################
        ##  TEST WITH PARAMS
        #########################

        base85_code = obfu.base85_encode(code)

        for encoded_code in (base85_code, obfu.code):
            self.assertRegex(
                encoded_code,
                "^from base64 import b85decode;exec[(]b85decode[(]b'.*'[)].decode[(][)]{2}$",
                "base85_encode don't return the good python code",
            )
            exec(encoded_code)

            self.assertEqual(
                environ["test"],
                "Python Hello World !",
                "base85_encode don't execute the good python code",
            )

    def test_xor_code(self):
        def input(string):
            return "abc"

        mock1 = Mock()
        mock2 = Mock()
        mock1.level = 0
        mock2.level = 6

        mock1.code = "environ['test'] = 'Hello World !'"
        mock1.password = None
        non_obfu_code1_length = len(mock1.code)

        self.assertEqual(
            Obfuscator.xor_code(mock1),
            "environ['test'] = 'Hello World !'",
            "xor_code change code with level 0",
        )
        mock1.level = 6

        mock2.code = "environ['test'] = 'Hello World !'"
        mock2.password = "abc"

        code = "environ['test'] = 'Python Hello World !'"
        non_obfu_code2_length = len(code)

        obfu1 = Obfuscator("")
        obfu2 = Obfuscator("", password="abc")
        xor_code1 = Obfuscator.xor_code(mock1)
        xor_code2 = Obfuscator.xor_code(mock2)

        #########################
        ##  TEST WITHOUT PARAMS AND PASSWORD
        #########################

        for cipher_code in (xor_code1, mock1.code):
            regexs = (
                (
                    "^_=\[([0-9]{1,3}(,[ ])?){40}\];__=len[(]_[)];___=exec;_____"
                    "='';\nfor _______,______ in enumerate[(]\[([0-9]{1,3}(,[ ])?)"
                    "{size}\][)]:_____\+=chr"
                    "[(]______\^_\[_______%__\][)]\n___[(]_____[)]$"
                )
                .replace("size", str(non_obfu_code1_length))
                .split("\n")
            )

            lines = cipher_code.split("\n")

            for line, regex in zip(lines, regexs):
                self.assertRegex(
                    line,
                    regex,
                    "xor_code don't return the good python code",
                )

            exec(cipher_code)

            self.assertEqual(
                environ["test"],
                "Hello World !",
                "xor_code don't execute the good python code",
            )

        #########################
        ##  TEST WITHOUT PARAMS, WITH PASSWORD
        #########################

        for cipher_code in (xor_code2, mock2.code):
            regexs = (
                (
                    "^_=input[(]'Password: '[)].encode[(][)];__=len[(]_[)];___=exec;_____"
                    "='';\nfor _______,______ in enumerate[(]\[([0-9]{1,3}(,[ ])?)"
                    "{size}\][)]:_____\+=chr"
                    "[(]______\^_\[_______%__\][)]\n___[(]_____[)]$"
                )
                .replace("size", str(non_obfu_code2_length))
                .split("\n")
            )

            lines = cipher_code.split("\n")

            for line, regex in zip(lines, regexs):
                self.assertRegex(
                    line,
                    regex,
                    "xor_code don't return the good python code",
                )

            exec(cipher_code)

            self.assertEqual(
                environ["test"],
                "Hello World !",
                "xor_code don't execute the good python code",
            )

        #########################
        ##  TEST WITH PARAMS, WITHOUT PASSWORD
        #########################

        xor_code1 = obfu1.xor_code(code)

        for cipher_code in (xor_code1, obfu1.code):
            regexs = (
                (
                    "^_=\[([0-9]{1,3}(,[ ])?){40}\];__=len[(]_[)];___=exec;_____"
                    "='';\nfor _______,______ in enumerate[(]\[([0-9]{1,3}(,[ ])?)"
                    "{size}\][)]:_____\+=chr"
                    "[(]______\^_\[_______%__\][)]\n___[(]_____[)]$"
                )
                .replace("size", str(non_obfu_code2_length))
                .split("\n")
            )

            lines = cipher_code.split("\n")

            for line, regex in zip(lines, regexs):
                self.assertRegex(
                    line,
                    regex,
                    "xor_code don't return the good python code",
                )

            exec(cipher_code)

            self.assertEqual(
                environ["test"],
                "Python Hello World !",
                "xor_code don't execute the good python code",
            )

        #########################
        ##  TEST WITH PARAMS AND PASSWORD
        #########################

        xor_code2 = obfu2.xor_code(code)

        for cipher_code in (xor_code2, obfu2.code):
            regexs = (
                (
                    "^_=input[(]'Password: '[)].encode[(][)];__=len[(]_[)];___=exec;_____"
                    "='';\nfor _______,______ in enumerate[(]\[([0-9]{1,3}(,[ ])?)"
                    "{size}\][)]:_____\+=chr"
                    "[(]______\^_\[_______%__\][)]\n___[(]_____[)]$"
                )
                .replace("size", str(non_obfu_code2_length))
                .split("\n")
            )

            lines = cipher_code.split("\n")

            for line, regex in zip(lines, regexs):
                self.assertRegex(
                    line,
                    regex,
                    "xor_code don't return the good python code",
                )

            exec(cipher_code)

            self.assertEqual(
                environ["test"],
                "Python Hello World !",
                "xor_code don't execute the good python code",
            )

    def test_visit_Constant(self):
        constant1 = ast.Constant(value="abc")
        constant2 = ast.Constant(value=b"abc")
        constant3 = ast.Constant(value=2)

        obfu = Obfuscator("", level=0)
        obfu.get_random_name("xor")
        obfu.init_crypt_strings()
        constant = obfu.visit_Constant(constant1)
        self.assertEqual(
            constant.value, "abc", "visit_Constant change code with level 0"
        )
        obfu.level = 6

        call1 = obfu.visit_Constant(constant1)
        call2 = obfu.visit_Constant(constant2)
        constant3_bis = obfu.visit_Constant(constant3)

        for constant in (call1, call2):
            self.assertIsInstance(
                constant, ast.Call, "visit_Constant don't return a ast.Call."
            )

        self.assertEqual(
            b"abc",
            obfu.xor(call2.args[0].value),
            "visit_Constant don't return the good value with bytes",
        )
        self.assertEqual(
            "abc",
            obfu.xor(call1.func.value.args[0].value).decode(),
            "visit_Constant don't return the good value with str",
        )
        self.assertEqual(
            constant3.value, constant3_bis.value, "visit_Constant change integer value"
        )

    def test_visit_Module(self):
        (doc, *_), (body_without_doc, *_), module, obfu = builds()
        obfu.level = 0

        module_test = obfu.visit_Module(module)
        self.assertIn(
            doc, module_test.body, "visit_Module delete doc string with level 0"
        )

        obfu.level = 6
        module_test = obfu.visit_Module(module)

        self.assertNotIn(doc, module_test.body, "visit_Module don't delete doc string")
        self.assertListEqual(
            module_test.body,
            body_without_doc,
            "visit_Module don't delete only doc string",
        )

    def test_default_obfuscation(self):
        obfu = Obfuscator("test.py")
        default_code = (
            "from os import environ;environ['test']='default_obfuscation test'"
        )

        with open("test.py", "w") as file:
            file.write(default_code)

        obfu.default_obfuscation()

        self.assertTrue(
            obfu.using_default_obfu,
            "default_obfuscation don't set using_default_obfu to True",
        )
        self.assertTrue(
            path.isfile(obfu.output_filename),
            "default_obfuscation don't write the code",
        )
        self.assertTrue(
            path.isfile("deobfuscate.json"),
            "default_obfuscation don't write the deobfuscate file",
        )

        with open(obfu.output_filename) as file:
            code = file.read()

        self.assertNotEqual(
            code, default_code, "default_obfuscation don't obfuscate the code"
        )

        import test_obfu

        self.assertEqual(
            "default_obfuscation test",
            getattr(test_obfu, obfu.default_names["environ"].obfu_name)["TEST"],
            "default_obfuscation don't obfuscate the correctly/good code",
        )

        remove("test.py")
        remove("test_obfu.py")
        remove("deobfuscate.json")

    def test_get_attributes_from(self):
        obfu = Obfuscator("")
        mock1 = Mock()
        mock1.test_attr = True

        mock2 = Mock()
        mock2 = obfu.get_attributes_from(mock2, mock1)

        self.assertTrue(
            mock2.test_attr,
            "get_attributes_from don't set all attributes on the new object",
        )

    def test_delete_doc_string(self):
        (doc, *_), (body_without_doc, *_), ast_doc_string, obfu = builds()

        ast_test = obfu.delete_doc_string(ast_doc_string)

        self.assertNotIn(
            doc, ast_test.body, "delete_doc_string don't delete doc string"
        )
        self.assertListEqual(
            ast_test.body,
            body_without_doc,
            "delete_doc_string don't delete only doc string",
        )

    def test_delete_field(self):
        _, _, ast_with_body, obfu = builds()

        ast_without_body = obfu.delete_field(ast_with_body, "body")

        with self.assertRaises(AttributeError, msg="delete_field don't delete field"):
            ast_without_body.body

    def test_delete_annotations(self):
        _, _, ast_with_annotation, obfu = builds()

        ast_without_annotation = obfu.delete_field(ast_with_annotation, "annotation")

        with self.assertRaises(
            AttributeError, msg="delete_annotations don't delete annotations"
        ):
            ast_without_annotation.annotation

    def test_delete_returns(self):
        _, _, ast_with_returns, obfu = builds()

        ast_without_returns = obfu.delete_field(ast_with_returns, "returns")

        with self.assertRaises(
            AttributeError, msg="delete_returns don't delete returns"
        ):
            ast_without_returns.returns

    def test_get_targets_and_value_from_import_from(self):
        elements = [ast.alias(name="dump"), ast.alias(name="Assign", asname="custom")]
        module = "ast"

        obfu = Obfuscator("")
        obfu.get_random_name("xor")
        # init_obfu_names(obfu)
        obfu.init_vars()
        obfu.init_crypt_strings()
        targets, values = obfu.get_targets_and_value_from_import_from(module, elements)

        targets = obfu.visit(targets)
        values = obfu.visit(values)

        self.assertIsInstance(
            targets,
            ast.Tuple,
            "get_targets_and_value_from_import_from don't return ast.Tuple object",
        )
        self.assertIsInstance(
            values,
            ast.Tuple,
            "get_targets_and_value_from_import_from don't return ast.Tuple object",
        )

        for target in targets.elts:
            self.assertIn(
                obfu.obfu_names[target.id].name,
                [
                    element.__dict__.get("asname") or element.__dict__.get("name")
                    for element in elements
                ],
                "get_targets_and_value_from_import_from return bad obfu name in first tuple",
            )

        for value in values.elts:
            self.assertEqual(
                value.value.value.func.id,
                obfu.default_names["__import__"].obfu_name,
                "get_targets_and_value_from_import_from don't return import function in second tuple",
            )
            self.assertEqual(
                obfu.xor(value.value.value.args[0].func.value.args[0].value).decode(),
                module,
                "get_targets_and_value_from_import_from don't import the good function name in second tuple",
            )
            self.assertEqual(
                value.value.attr,
                "__dict__",
                "get_targets_and_value_from_import_from don't return obfu __dict__ name in second tuple",
            )
            self.assertIn(
                obfu.xor(value.slice.func.value.args[0].value).decode(),
                [element.name for element in elements],
                "get_targets_and_value_from_import_from don't import the good element name in second tuple",
            )

    def test_visit_Import(self):
        import1 = ast.Import(names=[ast.alias(name="os"), ast.alias(name="sys")])

        obfu = Obfuscator("", level=0)
        obfu.init_crypt_strings()
        import1 = obfu.visit_Import(import1)

        self.assertIsInstance(
            import1,
            ast.Import,
            "visit_Import don't return an ast.Import object with level 0",
        )

        obfu.level = 6
        obfu.init_vars()
        assign = obfu.visit_Import(import1)

        self.assertIsInstance(
            assign, ast.Assign, "visit_Import don't return an ast.Assign object"
        )

        for name in assign.targets[0].elts:
            self.assertIn(
                obfu.obfu_names[name.id].name,
                ["os", "sys"],
                "visit_Import don't assign the good variable name",
            )

        for call in assign.value.elts:
            self.assertEqual(
                obfu.obfu_names[call.func.id].name,
                "__import__",
                "visit_Import don't call __import__ functions",
            )
            self.assertIn(
                obfu.xor(call.args[0].func.value.args[0].value).decode(),
                ["os", "sys"],
                "visit_Import don't import good module",
            )

    def test_visit_ImportFrom(self):
        import_from1 = ast.ImportFrom(
            module="dataclasses", names=[ast.alias(name="dataclass")], level=0
        )
        import_from2 = ast.ImportFrom(
            module="ast", names=[ast.alias(name="*")], level=0
        )

        ast_attr = [
            attr
            for attr in dir(ast)
            if not (attr.startswith("__") and attr.endswith("__"))
        ]

        obfu = Obfuscator("", level=0)
        obfu.init_crypt_strings()
        import_from1 = obfu.visit_ImportFrom(import_from1)
        self.assertIsInstance(
            import_from1,
            ast.ImportFrom,
            "visit_ImportFrom don't return an ast.ImportFrom object with level 0",
        )

        obfu.level = 6
        obfu.init_vars()
        assign = obfu.visit_ImportFrom(import_from1)

        self.assertIsInstance(
            assign, ast.Assign, "visit_ImportFrom don't return an ast.Assign object"
        )

        assign = obfu.visit_ImportFrom(import_from2)
        self.assertEqual(
            len(ast_attr),
            len(assign.targets[0].elts),
            "visit_ImportFrom don't import all attributes when import *",
        )
        obfu_ast_attr = [obfu.default_names[attr].obfu_name for attr in ast_attr]
        self.assertListEqual(
            obfu_ast_attr,
            [name.id for name in assign.targets[0].elts],
            "visit_ImportFrom don't import good attributes when import *",
        )

    def test_init_vars(self):
        global default_dir

        obfu = Obfuscator("")
        builtins_obfu = obfu.init_vars()

        elements = (
            list(globals()["__builtins__"].keys())
            if isinstance(__builtins__, dict)
            else dir(__builtins__)
        ) + default_dir

        self.assertEqual(
            builtins_obfu,
            obfu._dir_definition,
            "return value of init_vars is different than Obfuscator._dir_definition",
        )

        builtins_obfu = builtins_obfu.split("\n")[0]
        obfu_builtins, builtins = builtins_obfu.split("=")
        builtins, obfu_builtins = builtins.split(","), obfu_builtins.split(",")

        self.assertEqual(
            len(builtins),
            len(obfu_builtins),
            "len(builtins) is not equal to len(obfu_builtins) in init_vars",
        )

        for i, obfu_name in enumerate(obfu_builtins):
            self.assertEqual(
                builtins[i],
                obfu.obfu_names[obfu_name].name,
                "order of builtins or obfuscate_name is not good",
            )
            self.assertIn(
                builtins[i], elements, f"{builtins[i]} isn't in defaults variables"
            )

    def test_init_crypt_strings(self):
        obfu1 = Obfuscator("")
        code1 = obfu1.init_crypt_strings()

        obfu2 = Obfuscator("")
        code2 = obfu2.init_crypt_strings("abc='abc'")

        for code, obfu in ((code1, obfu1), (code2, obfu2)):
            self.assertIsNotNone(
                obfu._xor_password_key, "init_crypt_strings don't set the xor key"
            )
            self.assertEqual(
                len(obfu._xor_password_key),
                obfu._xor_password_key_length,
                "init_crypt_strings don't set the xor key with good length",
            )

            self.assertRegex(
                code,
                "^xor=lambda bytes_:\(bytes\(\[x\^\[([0-9]{1,3}(,[ ])?){40}\]\[i%40\] for i,x in enumerate\(bytes_\)\]\)\)\n.*$",
                "init_crypt_strings don't return the good code",
            )

            exec(code)
            encrypt = eval("xor(b'abc')")
            self.assertEqual(
                len(encrypt),
                3,
                "init_crypt_strings don't define xor lambda function",
            )
            self.assertEqual(
                eval(f"xor({encrypt})"),
                b"abc",
                "init_crypt_strings don't decrypt correctly an encrypted bytes",
            )

    def test_xor(self):
        obfu = Obfuscator("")

        with self.assertRaises(
            ObfuscationError,
            msg="xor don't raise ObfuscationError when _xor_password_key is None",
        ):
            obfu.xor(b"abc")

        obfu.init_crypt_strings()

        self.assertEqual(
            obfu.xor(obfu.xor(b"abc")),
            b"abc",
            "xor don't decrypt correctly an encrypted bytes",
        )

    def test_visit_ClassDef(self):
        class_ = ast.ClassDef(
            name="Test",
            bases=[ast.Name(id="Classe", ctx=ast.Load())],
            keywords=[],
            body=[ast.Expr(value=ast.Constant(value=" Doc String "))],
            decorator_list=[],
        )

        obfu = Obfuscator("", level=0)
        class_ = obfu.visit_ClassDef(class_)

        self.assertEqual(
            class_.name, "Test", "visit_ClassDef change the class name with level 0"
        )
        self.assertEqual(
            len(class_.body), 1, "visit_ClassDef delete doc string with level 0"
        )

        obfu.level = 6
        class_ = obfu.visit_ClassDef(class_)

        self.assertEqual(len(class_.body), 0, "visit_ClassDef don't delete doc string")
        self.assertNotEqual(
            class_.name, "Test", "visit_ClassDef don't change the class name"
        )
        self.assertEqual(
            obfu.default_names["Test"].obfu_name,
            class_.name,
            "visit_ClassDef the new class name is bad",
        )
        self.assertEqual(
            obfu.obfu_names[class_.name].name,
            "Test",
            "visit_ClassDef the new class name is bad",
        )

    def test_visit_FunctionDef(self):
        function1 = ast.FunctionDef(
            name="__init__",
            args=ast.arguments(
                posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]
            ),
            body=[ast.Expr(value=ast.Constant(value=" Doc String "))],
            decorator_list=[],
        )

        function2 = ast.FunctionDef(
            name="init",
            args=ast.arguments(
                posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]
            ),
            body=[ast.Expr(value=ast.Constant(value=" Doc String "))],
            decorator_list=[],
        )

        obfu = Obfuscator("", level=0)
        function = obfu.visit_FunctionDef(function2)
        self.assertEqual(
            function.name,
            "init",
            "visit_FunctionDef change the function name with level 0",
        )
        self.assertEqual(
            len(function.body), 1, "visit_FunctionDef delete doc string with level 0"
        )

        obfu.level = 6

        function = obfu.visit_FunctionDef(function2)
        self.assertEqual(
            len(function.body), 0, "visit_FunctionDef don't delete doc string"
        )
        self.assertNotEqual(
            function.name, "init", "visit_FunctionDef don't change the function name"
        )
        self.assertEqual(
            obfu.default_names["init"].obfu_name,
            function.name,
            "visit_FunctionDef the new function name is bad",
        )
        self.assertEqual(
            obfu.obfu_names[function.name].name,
            "init",
            "visit_FunctionDef the new function name is bad",
        )

        function = obfu.visit_FunctionDef(function1)
        self.assertEqual(
            function.name,
            "__init__",
            "visit_FunctionDef change the magic function name",
        )

    def test_visit_Name(self):
        name = ast.Name(id="name", ctx=ast.Store())

        obfu = Obfuscator("", level=0)
        name = obfu.visit_Name(name)
        self.assertEqual(name.id, "name", "visit_Name change Name.id with level 0")

        obfu.level = 6
        name = obfu.visit_Name(name)

        self.assertEqual(
            obfu.default_names["name"].obfu_name,
            name.id,
            "visit_Name don't return a Name with a good id",
        )

    def test_visit_Global(self):
        names = ["f0", "f1"]
        global_ = ast.Global(names=names.copy())

        obfu = Obfuscator("", level=0)
        global_ = obfu.visit_Global(global_)
        self.assertListEqual(
            global_.names, names, "visit_Global change names with level 0"
        )

        obfu.level = 6
        global_ = obfu.visit_Global(global_)

        for i, name in enumerate(global_.names):
            self.assertIn(
                obfu.obfu_names[name].name,
                names,
                "visit_Global don't return good obfuscate names",
            )
            self.assertEqual(
                obfu.obfu_names[name].name,
                f"f{i}",
                "visit_Global don't return names with good order",
            )

    def test_visit_arg(self):
        arg = ast.arg(arg="arg", annotation=ast.Name(id="str", ctx=ast.Load()))

        obfu = Obfuscator("", level=0)
        arg = obfu.visit_arg(arg)

        self.assertIsNotNone(arg.annotation, "visit_arg delete annotation with level 0")
        self.assertEqual(
            arg.annotation.id, "str", "visit_arg change annotation with level 0"
        )

        obfu.level = 6
        arg = obfu.visit_arg(arg)

        self.assertIsNone(arg.annotation, "visit_arg don't delete annotation")
        self.assertEqual(
            obfu.default_names["arg"].obfu_name,
            arg.arg,
            "visit_arg don't return arg(object) with good arg(attribute)",
        )

    def test_visit_AnnAssign(self):
        assign = ast.AnnAssign(
            target=ast.Name(id="abc", ctx=ast.Store()),
            annotation=ast.Name(id="str", ctx=ast.Load()),
            value=ast.Constant(value="abc"),
            simple=1,
        )

        obfu = Obfuscator("", level=0)
        assign = obfu.visit_AnnAssign(assign)

        self.assertIsInstance(
            assign,
            ast.AnnAssign,
            "visit_AnnAssign change AnnAssign object with level 0",
        )

        obfu.level = 6
        obfu.init_crypt_strings()
        assign = obfu.visit_AnnAssign(assign)

        self.assertIsInstance(
            assign, ast.Assign, "visit_AnnAssign don't build Assign object"
        )
        self.assertEqual(
            obfu.obfu_names[assign.targets[0].id].name,
            "abc",
            "visit_AnnAssign don't assign the good variable name",
        )
        self.assertEqual(
            obfu.xor(assign.value.func.value.args[0].value).decode(),
            "abc",
            "visit_AnnAssign don't assign the good value",
        )

    def test_write_deobfuscate(self):
        obfu = Obfuscator("test.py", names={"a": Name("a", "b", False, None)})
        obfu.write_deobfuscate()

        self.assertTrue(
            path.isfile("deobfuscate.json"),
            "write_deobfuscate don't create deobfuscate file",
        )

        with open("deobfuscate.json") as file:
            config = json.load(file)

        self.assertDictEqual(
            config["names"][0],
            {
                "name": "a",
                "obfuscation_name": "b",
                "definition": False,
                "namespace": None,
            },
            "write_deobfuscate don't write good names.",
        )
        self.assertIsNone(config["xor_encrypt"]["key"])
        self.assertDictEqual(
            config["Obfuscator"],
            {
                "level": 6,
                "default_obfuscation": False,
                "encoding": "utf-8",
                "output_file": "test_obfu.py",
            },
        )

        remove("deobfuscate.json")
        obfu.deobfuscate_file = False

        self.assertFalse(
            path.isfile("deobfuscate.json"),
            "write_deobfuscate create deobfuscate file when deobfuscate is desactivated",
        )

    def test_add_builtins(self):
        obfu = Obfuscator("")

        with self.assertRaises(
            ObfuscationError,
            msg="add_builtins don't raise Error if _dir_definition isn't defined",
        ):
            obfu.add_builtins()

        obfu._dir_definition = "p=print\n"

        with self.assertRaises(
            ObfuscationError, msg="add_builtins don't raise Error if code isn't defined"
        ):
            obfu.add_builtins()

        obfu.code = "p('Hello World !')"
        obfu.add_builtins()

        self.assertEqual(
            obfu.code,
            "p=print\n" + "p('Hello World !')",
            "add_builtins don't return the good code",
        )

    def test_write_code(self):
        obfu = Obfuscator("")

        with self.assertRaises(
            ObfuscationError, msg="write_code don't raise Error if code isn't defined"
        ):
            obfu.write_code()

        obfu.code = "print('Hello World !')"

        code = obfu.write_code()

        self.assertEqual(
            code,
            obfu.code,
            "write_code don't return the good code",
        )

        with open("_obfu.py") as file:
            self.assertEqual(
                file.read(),
                obfu.code,
                "write_code don't write the good code",
            )

        remove("_obfu.py")


def init_obfu_names(obfu):
    for name in dir(__builtins__):
        obfu.get_random_name(name)


def builds():
    doc = ast.Expr(value=ast.Constant(value="abc"))
    false_doc = ast.Expr(value=Mock())

    AST_test = ast.AST(
        body=[doc, false_doc], annotation="annotation", returns=ast.Constant(value=None)
    )
    AST_test._fields = tuple(AST_test.__dict__.keys())

    body_without_doc = AST_test.body.copy()
    body_without_doc.remove(doc)

    obfu = Obfuscator("")
    obfu.init_crypt_strings()

    return (doc, false_doc), (body_without_doc,), AST_test, obfu


def write_ast():
    with open("code_using_for_test.py") as file:
        python_code = file.read()

    ast_code = ast.parse(python_code)

    with open("ast_code_using_for_test.py", "w") as file:
        file.write(ast.dump(ast_code, indent=4))


if __name__ == "__main__":
    # write_ast()
    unittest.main()

    """
        - Check if all functions are tested
        - Check if all fonctionnalities are tested in all functions
        - Test commands lines and executables
    """
