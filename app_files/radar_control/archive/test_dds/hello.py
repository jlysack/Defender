#!/usr/bin/env python3

# hello.py 
import rti.types as idl 

@idl.struct
class HelloWorld:
    message: str = "" 
