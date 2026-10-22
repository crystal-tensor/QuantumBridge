# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Public QPY v13 arithmetic replay protocol, implemented independently.

import math
import operator
import struct
from numbers import Complex, Integral, Real
from uuid import UUID
from quantumbridge.core import Parameter, ParameterExpression
from .limits import SerializationLimits
from .errors import UnsupportedFeature, FormatValidationError

RECORD = struct.Struct("!Bc16sc16s")
BINARY = {0:operator.add,1:operator.sub,2:operator.mul,3:operator.truediv,4:operator.pow,
          18:lambda left,right:right-left,19:lambda left,right:right/left,20:lambda left,right:right**left}
OPCODES = {"+":0,"-":1,"*":2,"/":3,"**":4}
UNARY = {5:"sin",6:"cos",7:"tan",8:"arcsin",9:"arccos",10:"exp",11:"log",
         12:"sign",14:"conjugate",16:"abs",17:"arctan"}
UNARY_CODES = {name:code for code,name in UNARY.items()}


def read_expression(reader):
    count,size = reader.unpack("!QQ")
    reader.bounded("max_parameter_nodes",count)
    if size % RECORD.size: reader.error("Misaligned symbolic replay payload.")
    reader.bounded("max_parameter_nodes",size//RECORD.size)
    replay = reader.take(size)
    symbols = {}
    for _ in range(count):
        key_type,value_type,value_size = reader.unpack("!ccQ")
        if key_type==b"v":
            key=reader.parameter_vector()
            uid=UUID(key.uuid).bytes
        elif key_type==b"p":
            name_size,uid = reader.unpack("!H16s")
            name = reader.text(name_size)
            uid_text = str(UUID(bytes=uid))
            if not name or name in reader.parameters and (type(reader.parameters[name]) is not Parameter or reader.parameters[name].uuid != uid_text):
                reader.error("Conflicting symbolic parameter identities.")
            key = reader.parameters.setdefault(name,Parameter(name,uid_text))
        else:reader.error("Unsupported parameter symbol type.",UnsupportedFeature)
        if uid in symbols: reader.error("Duplicate symbolic mapping key.")
        if value_type in {b"p",b"v"}:
            if value_type!=key_type:reader.error("Symbolic parameter alias type does not match its key.")
            if value_size: reader.error("Parameter alias must have zero payload bytes.")
            value = key
        else: value = reader.value(value_type,value_size)
        symbols[uid] = value
    stack = []
    def operand(kind,data):
        if kind == b"n":
            if data != bytes(16) or not stack: reader.error("Invalid symbolic replay stack reference.")
            return stack.pop()
        if kind == b"p":
            if data not in symbols: reader.error("Symbolic replay references unknown UUID.")
            return symbols[data],1
        if kind in {b"i",b"f"}:
            if data[:8] != bytes(8): reader.error("Invalid numeric symbolic padding.")
            value, = struct.unpack("!q" if kind == b"i" else "!d",data[8:])
            if not math.isfinite(value): reader.error("Nonfinite symbolic literal.")
            return value,1
        if kind == b"c":
            real,imag = struct.unpack("!dd",data)
            if not math.isfinite(real) or not math.isfinite(imag): reader.error("Nonfinite symbolic literal.")
            return complex(real,imag),1
        reader.error(f"Unsupported symbolic operand {kind!r}.",UnsupportedFeature)
    for offset in range(0,len(replay),RECORD.size):
        op,left_kind,left_data,right_kind,right_data = RECORD.unpack_from(replay,offset)
        if op in UNARY:
            if right_kind != b"n" or right_data != bytes(16): reader.error("Unary symbolic replay has an unexpected right operand.")
            left,ld = operand(left_kind,left_data)
            reader.bounded("max_symbolic_expression_depth",ld+1)
            from quantumbridge.core.parameters import _coerce_expression
            try: value = getattr(_coerce_expression(left),UNARY[op])()
            except (ArithmeticError,TypeError,ValueError) as exc: reader.error(f"Invalid symbolic function: {type(exc).__name__}.")
            stack.append((value,ld+1))
            continue
        if op not in BINARY: reader.error(f"Unsupported symbolic replay opcode {op}.",UnsupportedFeature)
        right,rd = operand(right_kind,right_data)
        left,ld = operand(left_kind,left_data)
        depth = 1+max(ld,rd)
        reader.bounded("max_symbolic_expression_depth",depth)
        base,exponent = (right,left) if op == 20 else (left,right)
        if op in {4,20} and isinstance(base,Integral) and isinstance(exponent,Integral) and exponent > 0 and max(1,base.bit_length())*exponent > 4096:
            reader.error("Numeric symbolic power exceeds the integer budget.")
        try: value = BINARY[op](left,right)
        except (ArithmeticError,TypeError,ValueError) as exc: reader.error(f"Invalid symbolic arithmetic: {type(exc).__name__}.")
        if isinstance(value,Real) and not math.isfinite(value): reader.error("Nonfinite symbolic arithmetic.")
        stack.append((value,depth))
    if len(stack) != 1: reader.error("Symbolic replay must yield exactly one expression.")
    return stack[0][0]


def write_expression(expression,limits=None):
    from .qpy import _uid, _parameter_value
    limits = limits or SerializationLimits()
    records = []
    symbols = {}
    def emit(value,depth=0):
        limits.check("max_symbolic_expression_depth",depth,format="qpy",version=13)
        if isinstance(value,Parameter):
            symbols[value.name] = value
            return b"p",_uid(value).bytes
        if isinstance(value,ParameterExpression):
            if value.op in {"const","parameter"}: return emit(value.args[0],depth+1)
            if value.op == "neg": return emit(value.args[0] * -1,depth+1)
            if value.op in UNARY_CODES:
                left = emit(value.args[0],depth+1)
                limits.check("max_parameter_nodes",len(records)+1,format="qpy",version=13)
                records.append(RECORD.pack(UNARY_CODES[value.op],*left,b"n",bytes(16)))
                return b"n",bytes(16)
            if value.op not in OPCODES: raise UnsupportedFeature("Unsupported arithmetic expression opcode.",format="qpy",version=13)
            left = emit(value.args[0],depth+1)
            right = emit(value.args[1],depth+1)
            records.append(RECORD.pack(OPCODES[value.op],*left,*right))
            limits.check("max_parameter_nodes",len(records),format="qpy",version=13)
            return b"n",bytes(16)
        if isinstance(value,Integral) and not isinstance(value,bool): return b"i",bytes(8)+struct.pack("!q",int(value))
        if isinstance(value,Real) and math.isfinite(value): return b"f",bytes(8)+struct.pack("!d",float(value))
        if isinstance(value,Complex) and math.isfinite(value.real) and math.isfinite(value.imag):
            return b"c",struct.pack("!dd",value.real,value.imag)
        raise UnsupportedFeature("Unsupported symbolic arithmetic value.",format="qpy",version=13)
    emit(expression)
    if not records: raise FormatValidationError("Symbolic replay requires an arithmetic operation.",format="qpy",version=13)
    mapping = []
    for name,parameter in sorted(symbols.items()):
        kind,payload = _parameter_value(parameter,limits)
        mapping.extend((struct.pack("!ccQ",kind,kind,0),payload))
    return struct.pack("!QQ",len(symbols),len(records)*RECORD.size)+b"".join(records+mapping)
