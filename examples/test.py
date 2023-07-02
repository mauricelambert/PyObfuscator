"""
Doc String du module

python3 ..\\PyObfuscator.py -o test_level1.py -l 1 test.py
python3 ..\\PyObfuscator.py -o test_level2.py -l 2 test.py
python3 ..\\PyObfuscator.py -o test_level3.py -l 3 test.py
python3 ..\\PyObfuscator.py -o test_level4.py -l 4 test.py
python3 ..\\PyObfuscator.py -o test_level5.py -l 5 test.py
python3 ..\\PyObfuscator.py -o test_level6.py -l 6 test.py
"""

from abc import ABC as DefaultABC
from dataclasses import dataclass
from contextlib import suppress, contextmanager
from sys import *
import os, sys

obfu_os, obfu_suppress = __import__("os"), __import__("contextlib").__dict__["suppress"]

obfu_os = __import__("os")
obfu_suppress = __import__("contextlib").__dict__["suppress"]

assert os == obfu_os
assert obfu_suppress == suppress
assert obfu_suppress != os


@dataclass
class Classe(DefaultABC):

    abc: str = "abc"


class Classe2(Classe):

    def __init__(self):
        self.abc2: str = "abc"


class Test(Classe2):

    """Doc String de Test"""

    def __init__(self, string: str):

        """ Doc String de __init__ """

        #breakpoint()
        #super().__init__() ## THIS LINE RETURN AN ERROR
        super(self.__class__, self).__init__()
        self.string: str = string
        ## "self.abc" RETURN AN ERROR
        self.abc2

    def function(self, *args, integer: int = 5, **kwargs) -> None:

        """ Doc de function """

        for arg in args:
            print(arg)  # affiche l'argument
            continue

        print(integer)  # affiche l'entier

        for k, v in kwargs.items():
            print(k, v)  # affiche la clés et la valeur
            del kwargs[k]
            break

        print(self.string)  # affiche la string
        print(self.abc2)  # affiche la string

        return None

    def keywords(self):

        """ Tests all python keywords. """

        def test(string):
            return string

        global f
        f = lambda x: (x * 2)
        test(f(b'abc').decode("utf-8"))

        self.string += f(self.string)
        self.abc2 += f(self.abc2)
        abc = self.abc2

        if abc := "abc" and self.string == self.string:
            pass
        elif self.abc2 is None or self.string is not None:
            False
        elif True:
            pass

        assert abc != ""

        try:
            abc
        except NameError:
            raise NameError("abc is not define")
        finally:
            print(self.abc2)

        drapeau = True
        while drapeau:
            drapeau = False
            with suppress(NameError):
                yield abc

        yield self.abc2
        yield self.string


if __name__ == "__main__":
    test = Test("string")
    test.function("a", "b", "c", integer=3, cles="value")

    for string in test.keywords():
        print(string)

    argv # test sys import
    stdout # test sys import

    os # test import
    sys # test import

    my_bin = 0b01010
    my_int = 145
    my_float = 145.5
    my_hexa = 0xa6
    my_bytes = b"abc"

    my_list = [1,2,3]
    my_set = {1,2,3}
    my_dict = {1:1,2:3,3:2}
