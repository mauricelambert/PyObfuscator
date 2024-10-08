![PyObfuscator logo](https://mauricelambert.github.io/info/python/security/PyObfuscator3_small.png "PyObfuscator logo")

# PyObfuscator

## Description

This tool obfuscates python code.

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
PyObfuscator -h      # help message
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
python3 -m doctest -v PyObfuscator.py
python3 -m unittest discover -s tests -p Test*.py -v
python3 -m coverage report
```

## Bugs

### Python version

Be careful with environment, the python version used to obfuscate the code should be used to execute it, because `builtins` methods can be differents. Example using `python3.11` to obfuscate a code and using `python3.8` to execute the obfuscation:

```
Traceback (most recent call last):
  File "examples/test_level2.py", line 1, in <module>
    FDPNIhb1AZEN,seksF21wjxt5,xqWjyUJQi2WW,uek5BUS_9gp9,DUf2SsKgzwIR,UeB2l_bNCh3N,u_n3FMDZm8tq,feUH2QpjE1gi,hA33zmiTJ_JE,M3lzh7eBSD9y,NuY_a_VBO50V,lgOF8wmF3ql4,evF7Z_VpmU_w,rAD4vYkZfTqs,A3d0EhLPyeE1,NCzfbX1s_ggE,CriWabrsNFfO,XkjAnTEaNfuZ,BOqlKFTYkxbk,y2Dt_mc2THTA,Rp6gDOiPNDue,Gfg2DqYJjCzi,c8wWtRA76FdT,Cq2Su4t4y0h4,fbbaDgxs8tWM,R6tcHR8knbgb,qhyLkEbSFB4S,Bh3PAjtAs_ro,EhDsQ7NUGiS8,mFOzzhayukZF,RzLj02zhQOac,rTHnxBm852It,fQfaXvdfr51h,OwN8fPlvvHio,ou9uh1HSaZ_h,cQHwbRxoIABE,gO9zG8s9hQ85,jG7_ouSPtcJD,Rrz6wtYDgLyh,SepJ1GH_EvbO,CmEouI596SfP,cdjga9FvDMrR,xXKwxO3Af6ZC,IlSqIRFUc3aq,eiK3E54SxbFL,T_nEHJVrd8xa,dyeFfvNvRrJe,nQ3aG44kYDrE,d79KCDSODUdp,v8Ih6eJzsZct,mBDQlvTLhz5_,ifXIJVCat530,GCso0nOOcTvs,vjduw9_bYMAC,RpDzd9pIuzsp,HY0EPrDGTokL,giYP_dZTTiBY,blL25OfKbP_r,ocO5loEcx20N,AZp_GuYUG7qv,_DCe2Pf05TXF,qeY3dofBohyR,RylQla9TlcNg,g7jtp3n62w5F,FrJC6cWPgiE2,jnfMTOrLcfqd,cnMq4yvWy3GW,iPmZyGtZMhz7,OcgS6nKP_s5X,jaqISdaRa0ew,uO41PEYi7HMu,AZBUShNdIuX5,s2rqHmFMnwH1,XPJarUBiJk7D,e0SXoCio_DWE,w17jY9PSTodx,t2bSK98RFzM_,Qkp8QP0cUTaG,yT2XPV9tzlXx,tWeUmmgtidl3,mbjQPtxtxP7G,JxQvQeWBKRPi,zoQ5baLbTfil,nZoIdYSG5kFr,iVCjamAO6XIn,Tto8NZRTYO72,GHFFxAReo1VB,mq8K2uzcjw7t,pKf7VEb4p6dI,xpHqiVjNS4lX,CJru0K1uWKzM,m1efM_Co0gSv,UK3DqzeZ74rh,VZR0NBMxiWaq,vUz2dlBx9yvi,HP9lXICmFjl9,kOF5lxeAR_ag,RFPMvZDIZBM4,IwRGhMx782L6,R6I1WOjRiEY3,pXZGyDO5POgg,Mmh3GIH0pn9g,QIHGG3kvbTDT,SnqQLHu_oegW,v3JLevaT8dFE,dot2SSVbimus,h0F6lqwWBnTz,WZfDRY4jqD9i,GaCJ66MKZ7z5,O12mBRro2EjY,oOjJs6N8kdLR,Ih0Qk_Jf5txk,pbGaW1lwTTZQ,YvHk6bp91YLQ,nC1x2GGo_x3K,A440BaO7Yb_5,BBdxdBzon96y,b1hNtXENuzuh,MQDqjzcYElA7,p9VtLdxESgWm,nCtRO2HjFujc,sU7fWucgGmHg,X3_YNBBM7YGH,TQjjgn8BRnDS,Ikh4dRElUDTk,TrnUtcs8WS3k,M7bn5Vrg3OGY,IR8uzG04ar89,GCKHIADb6Wnv,PPTwFCzsLZZA,NhT3ESD2opiP,S7HSHlLGnHYd,GkkQa2mEOp7r,wW8UFW6MMSfV,nRnBtNqQ0haa,XzDeNchDhUFa,MQ8HU46biWT5,CQg_VvjuAcZW,dZ38dwV3zvkX,_9Q2HZjaOLuy,XEvrxUAzCWg9,aPu2QDS0jErQ,Ta60wzRxmZbF,qsBi0eW1wbw0,QypXydiMEfUM,e9AQ2_aOuA6q,yuTgsIloXhqk,qfkiotz2gFQy,u3ciCSnQCsWs,zyHM8gHWxyAO,iTs_Rdx40gau,sUKE7PHxzi8g,FmrWkwmzE4g7,KtRksPeReH51,k0sEHlvTMXPs,PgCfUfZlha8S,mDMspkh5l4LM,L5eUGEzsyNao,lYEOTtozCnvK,Uypmnv6RLVw4,t2bSK98RFzM_,ZfXs5cUjR9pI,yT2XPV9tzlXx,tWeUmmgtidl3,mbjQPtxtxP7G,JxQvQeWBKRPi=ArithmeticError,AssertionError,AttributeError,BaseException,BaseExceptionGroup,BlockingIOError,BrokenPipeError,BufferError,BytesWarning,ChildProcessError,ConnectionAbortedError,ConnectionError,ConnectionRefusedError,ConnectionResetError,DeprecationWarning,EOFError,Ellipsis,EncodingWarning,EnvironmentError,Exception,ExceptionGroup,False,FileExistsError,FileNotFoundError,FloatingPointError,FutureWarning,GeneratorExit,IOError,ImportError,ImportWarning,IndentationError,IndexError,InterruptedError,IsADirectoryError,KeyError,KeyboardInterrupt,LookupError,MemoryError,ModuleNotFoundError,NameError,None,NotADirectoryError,NotImplemented,NotImplementedError,OSError,OverflowError,PendingDeprecationWarning,PermissionError,ProcessLookupError,RecursionError,ReferenceError,ResourceWarning,RuntimeError,RuntimeWarning,StopAsyncIteration,StopIteration,SyntaxError,SyntaxWarning,SystemError,SystemExit,TabError,TimeoutError,True,TypeError,UnboundLocalError,UnicodeDecodeError,UnicodeEncodeError,UnicodeError,UnicodeTranslateError,UnicodeWarning,UserWarning,ValueError,Warning,ZeroDivisionError,__build_class__,__debug__,__doc__,__import__,__loader__,__name__,__package__,__spec__,abs,aiter,all,anext,any,ascii,bin,bool,breakpoint,bytearray,bytes,callable,chr,classmethod,compile,complex,copyright,credits,delattr,dict,dir,divmod,enumerate,eval,exec,exit,filter,float,format,frozenset,getattr,globals,hasattr,hash,help,hex,id,input,int,isinstance,issubclass,iter,len,license,list,locals,map,max,memoryview,min,next,object,oct,open,ord,pow,print,property,quit,range,repr,reversed,round,set,setattr,slice,sorted,staticmethod,str,sum,super,tuple,type,vars,zip,__annotations__,__builtins__,__cached__,__doc__,__file__,__loader__,__name__,__package__,__spec__
NameError: name 'BaseExceptionGroup' is not defined
```

The builtin `BaseExceptionGroup` does not exists in `python3.8` but it exists in `python3.11`.

### Pyinstaller

Be careful with pyinstaller or other way to freeze your app, somes variables exist in the default python interpreter but not in your freezed app. Set variables with default values to solve error (for pyinstaller):

```python
from sys import exit
copyright="""Copyright (c) 2001-2023 Python Software Foundation.
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

### Names obfuscation inter namespaces

It's probably very difficult to define statically type of each varaibles used. That cause a bug in the following code:

```python
from threading import Thread

class NotThread:
    def start():
        print("start")

Thread(target=start).start()
```

In the previous code all `start` attributes names will be obfuscated but the `threading.Thread` class in not obfuscated so it doesn't have the obfuscated `start` name as method, that cause the `AttributeError` (for example: `AttributeError: 'Thread' object has no attribute 'i3xEgmcuREyD'`).

To fix it you should have names differents than non-obfuscated names.

## Links

 - [Github Page](https://github.com/mauricelambert/PyObfuscator/)
 - [Documentation](https://mauricelambert.github.io/info/python/security/PyObfuscator.html)
 - [Download as python executable](https://mauricelambert.github.io/info/python/security/PyObfuscator.pyz)
 - [Pypi package](https://pypi.org/project/PyObfuscator/)
 - [Examples](https://github.com/mauricelambert/PyObfuscator/tree/main/examples)

## Licence

Licensed under the [GPL, version 3](https://www.gnu.org/licenses/).

