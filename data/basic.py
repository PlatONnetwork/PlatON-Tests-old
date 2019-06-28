wasm = {
    "basic": "./data/contract/basic.wasm"
}
abi = {
    "basic": "./data/contract/basic.cpp.abi.json"
}
contract_address = {
    "basic": "0x"
}

func = {
    "basic": [
        # int8###############################
        {
            "func": "test_set_arr_int8", "param":
            [
                {"type": "int8", "value": 1},
                {"type": "int8", "value": 1},
                {"type": "int8", "value": 1}
            ],
            "execpt": 1,
            "call_func": "test_get_arr_int8",
            "name": "正常输入",
        },
        {
            "func": "test_set_arr_int8", "param":
            [
                {"type": "int8", "value": 0},
                {"type": "int8", "value": 1},
                {"type": "int8", "value": 1}
            ],
            "execpt": 0,
            "call_func": "test_get_arr_int8",
            "name": "正常输入0",
        },
        {
            "func": "test_set_arr_int8", "param":
            [
                {"type": "int8", "value": -1},
                {"type": "int8", "value": 1},
                {"type": "int8", "value": 1}
            ],
            "execpt": -1,
            "call_func": "test_get_arr_int8",
            "name": "负数输入",
        },
        {
            "func": "test_set_arr_int8", "param":
            [
                {"type": "int8", "value": -127},
                {"type": "int8", "value": 1},
                {"type": "int8", "value": 1}
            ],
            "execpt": -127,
            "call_func": "test_get_arr_int8",
            "name": "负数最小输入",
        },
        {
            "func": "test_set_arr_int8", "param":
            [
                {"type": "int8", "value": 126},
                {"type": "int8", "value": 1},
                {"type": "int8", "value": 1}
            ],
            "execpt": 126,
            "call_func": "test_get_arr_int8",
            "name": "正数最大输入",
        },
        {
            "func": "test_set_arr_int8", "param":
            [
                {"type": "int16", "value": -200},
                {"type": "int8", "value": 1},
                {"type": "int8", "value": 1}
            ],
            "notevent": 1,
            "execpt": 126,
            "call_func": "test_get_arr_int8",
            "name": "负数溢出输入",
        },
        {
            "func": "test_set_arr_int8", "param":
            [
                {"type": "int16", "value": 200},
                {"type": "int8", "value": 1},
                {"type": "int8", "value": 1}
            ],
            "notevent": 1,
            "execpt": 126,
            "call_func": "test_get_arr_int8",
            "name": "正数溢出输入",
        },
        {
            "func": "test_set_arr_int8", "param":
            [
                {"type": "char", "value": "asd"},
                {"type": "int8", "value": 1},
                {"type": "int8", "value": 1}
            ],
            "notevent": 1,
            "execpt": 126,
            "call_func": "test_get_arr_int8",
            "name": "字符串输入",
        },
        # uint8#############################
        {
            "func": "test_set_arr_uint8", "param":
            [
                {"type": "uint8", "value": 1},
                {"type": "uint8", "value": 1},
                {"type": "uint8", "value": 1}
            ],
            "execpt": 1,
            "call_func": "test_get_arr_uint8",
            "name": "正常输入",
        },
        {
            "func": "test_set_arr_uint8", "param":
            [
                {"type": "uint8", "value": 0},
                {"type": "uint8", "value": 1},
                {"type": "uint8", "value": 1}
            ],
            "execpt": 0,
            "call_func": "test_get_arr_uint8",
            "name": "正常输入最小值",
        },
        {
            "func": "test_set_arr_uint8", "param":
            [
                {"type": "uint16", "value": 255},
                {"type": "uint8", "value": 1},
                {"type": "uint8", "value": 1}
            ],
            "execpt": 255,
            "call_func": "test_get_arr_uint8",
            "name": "正常输入最大值",
        },
        {
            "func": "test_set_arr_uint8", "param":
            [
                {"type": "int8", "value": -1},
                {"type": "uint8", "value": 1},
                {"type": "uint8", "value": 1}
            ],
            "notevent": 1,
            "execpt": 255,
            "call_func": "test_get_arr_uint8",
            "name": "负数输入",
        },
        {
            "func": "test_set_arr_uint8", "param":
            [
                {"type": "int16", "value": 257},
                {"type": "uint8", "value": 1},
                {"type": "uint8", "value": 1}
            ],
            "notevent": 1,
            "execpt": 255,
            "call_func": "test_get_arr_uint8",
            "name": "正数溢出输入",
        },
        {
            "func": "test_set_arr_uint8", "param":
            [
                {"type": "char", "value": "mynameis"},
                {"type": "uint8", "value": 1},
                {"type": "uint8", "value": 1}
            ],
            "notevent": 1,
            "execpt": 255,
            "call_func": "test_get_arr_uint8",
            "name": "字符串输入",
        },
        # int16#############################
        {
            "func": "test_set_arr_int16", "param":
            [
                {"type": "int16", "value": 1000},
                {"type": "int16", "value": 1000},
                {"type": "int16", "value": 1000}
            ],
            "execpt": 1000,
            "call_func": "test_get_arr_int16",
            "name": "正常输入",
        },
        {
            "func": "test_set_arr_int=16", "param":
            [
                {"type": "int16", "value": 0},
                {"type": "int16", "value": 11111},
                {"type": "int16", "value": 11111}
            ],
            "execpt": 0,
            "call_func": "test_get_arr_int16",
            "name": "正常输入0",
        },
        {
            "func": "test_set_arr_int16", "param":
            [
                {"type": "int16", "value": -1},
                {"type": "int16", "value": 11111},
                {"type": "int16", "value": 11111}
            ],
            "execpt": -1,
            "call_func": "test_get_arr_int16",
            "name": "负数输入",
        },
        {
            "func": "test_set_arr_int16", "param":
            [
                {"type": "int64", "value": -32768},
                {"type": "int16", "value": 1111},
                {"type": "int16", "value": 111}
            ],
            "execpt": -32768,
            "call_func": "test_get_arr_int16",
            "name": "负数最小输入",
        },
        {
            "func": "test_set_arr_int16", "param":
            [
                {"type": "int64", "value": 32767},
                {"type": "int16", "value": 11111},
                {"type": "int16", "value": 11111}
            ],
            "execpt": 32767,
            "call_func": "test_get_arr_int16",
            "name": "正数最大输入",
        },
        {
            "func": "test_set_arr_int16", "param":
            [
                {"type": "int64", "value": -32769},
                {"type": "int16", "value": 1111},
                {"type": "int16", "value": 1111}
            ],
            "notevent": 1,
            "execpt": 32767,
            "call_func": "test_get_arr_int16",
            "name": "负数溢出输入",
        },
        {
            "func": "test_set_arr_int16", "param":
            [
                {"type": "int64", "value": 32768},
                {"type": "int16", "value": 1},
                {"type": "int16", "value": 1}
            ],
            "notevent": 1,
            "execpt": 32767,
            "call_func": "test_get_arr_int16",
            "name": "正数溢出输入",
        },
        {
            "func": "test_set_arr_int16", "param":
            [
                {"type": "char", "value": "asd"},
                {"type": "int16", "value": 1},
                {"type": "int16", "value": 1}
            ],
            "notevent": 1,
            "execpt": 32767,
            "call_func": "test_get_arr_int16",
            "name": "字符串输入",
        },
        # uint16#############################
        {
            "func": "test_set_arr_uint16", "param":
            [
                {"type": "uint64", "value": 32767},
                {"type": "uint16", "value": 32767},
                {"type": "uint16", "value": 32767}
            ],
            "execpt": 32767,
            "call_func": "test_get_arr_uint16",
            "name": "正常输入",
        },
        {
            "func": "test_set_arr_uint16", "param":
            [
                {"type": "uint64", "value": 0},
                {"type": "uint16", "value": 1},
                {"type": "uint16", "value": 1}
            ],
            "execpt": 0,
            "call_func": "test_get_arr_uint16",
            "name": "正常输入最小值",
        },
        {
            "func": "test_set_arr_uint16", "param":
            [
                {"type": "uint64", "value": 65535},
                {"type": "uint16", "value": 11111},
                {"type": "uint16", "value": 11111}
            ],
            "execpt": 65535,
            "call_func": "test_get_arr_uint16",
            "name": "正常输入最大值",
        },
        {
            "func": "test_set_arr_uint16", "param":
            [
                {"type": "int16", "value": -1},
                {"type": "uint16", "value": 1},
                {"type": "uint16", "value": 1}
            ],
            "notevent": 1,
            "execpt": 65535,
            "call_func": "test_get_arr_uint16",
            "name": "负数输入",
        },
        {
            "func": "test_set_arr_uint16", "param":
            [
                {"type": "int64", "value": 65539},
                {"type": "uint16", "value": 111},
                {"type": "uint16", "value": 111}
            ],
            "notevent": 1,
            "execpt": 65535,
            "call_func": "test_get_arr_uint16",
            "name": "正数溢出输入",
        },
        {
            "func": "test_set_arr_uint16", "param":
            [
                {"type": "char", "value": "mynameis"},
                {"type": "uint16", "value": 1},
                {"type": "uint16", "value": 1}
            ],
            "notevent": 1,
            "execpt": 65535,
            "call_func": "test_get_arr_uint16",
            "name": "字符串输入",
        },
        # int32 ########################
        {
            "func": "test_set_arr_int32", "param":
            [
                {"type": "int32", "value": 1000},
                {"type": "int32", "value": 1000},
                {"type": "int32", "value": 1000}
            ],
            "execpt": 1000,
            "call_func": "test_get_arr_int32",
            "name": "正常输入",
        },
        {
            "func": "test_set_arr_int32", "param":
            [
                {"type": "int32", "value": 0},
                {"type": "int32", "value": 11111},
                {"type": "int32", "value": 11111}
            ],
            "execpt": 0,
            "call_func": "test_get_arr_int32",
            "name": "正常输入0",
        },
        {
            "func": "test_set_arr_int32", "param":
            [
                {"type": "int32", "value": -1},
                {"type": "int32", "value": 11111},
                {"type": "int32", "value": 11111}
            ],
            "execpt": -1,
            "call_func": "test_get_arr_int32",
            "name": "负数输入",
        },
        {
            "func": "test_set_arr_int32", "param":
            [
                {"type": "int64", "value": -2147483648},
                {"type": "int32", "value": 11111111},
                {"type": "int32", "value": 111111111}
            ],
            "execpt": -2147483648,
            "call_func": "test_get_arr_int32",
            "name": "负数最小输入",
        },
        {
            "func": "test_set_arr_int32", "param":
            [
                {"type": "int64", "value": 2147483647},
                {"type": "int32", "value": 111111111},
                {"type": "int32", "value": 11111111}
            ],
            "execpt": 2147483647,
            "call_func": "test_get_arr_int32",
            "name": "正数最大输入",
        },
        {
            "func": "test_set_arr_int32", "param":
            [
                {"type": "int64", "value": -2147483649},
                {"type": "int32", "value": 1111},
                {"type": "int32", "value": 1111}
            ],
            "notevent": 1,
            "execpt": 2147483647,
            "call_func": "test_get_arr_int32",
            "name": "负数溢出输入",
        },
        {
            "func": "test_set_arr_int32", "param":
            [
                {"type": "int64", "value": 2147483649},
                {"type": "int32", "value": 111111},
                {"type": "int32", "value": 1111111}
            ],
            "notevent": 1,
            "execpt": 2147483647,
            "call_func": "test_get_arr_int32",
            "name": "正数溢出输入",
        },
        {
            "func": "test_set_arr_int32", "param":
            [
                {"type": "char", "value": "asd"},
                {"type": "int32", "value": 1},
                {"type": "int32", "value": 1}
            ],
            "notevent": 1,
            "execpt": 2147483647,
            "call_func": "test_get_arr_int32",
            "name": "字符串输入",
        },
        # uint32#############################
        {
            "func": "test_set_arr_uint32", "param":
            [
                {"type": "uint64", "value": 32767},
                {"type": "uint32", "value": 32767},
                {"type": "uint32", "value": 32767}
            ],
            "execpt": 32767,
            "call_func": "test_get_arr_uint32",
            "name": "正常输入",
        },
        {
            "func": "test_set_arr_uint32", "param":
            [
                {"type": "uint64", "value": 0},
                {"type": "uint32", "value": 1},
                {"type": "uint32", "value": 1}
            ],
            "execpt": 0,
            "call_func": "test_get_arr_uint32",
            "name": "正常输入最小值",
        },
        {
            "func": "test_set_arr_uint32", "param":
            [
                {"type": "uint64", "value": 4294967295},
                {"type": "uint32", "value": 111111111},
                {"type": "uint32", "value": 111111111}
            ],
            "execpt": 4294967295,
            "call_func": "test_get_arr_uint32",
            "name": "正常输入最大值",
        },
        {
            "func": "test_set_arr_uint32", "param":
            [
                {"type": "int16", "value": -1},
                {"type": "uint32", "value": 1},
                {"type": "uint32", "value": 1}
            ],
            "notevent": 1,
            "execpt": 4294967295,
            "call_func": "test_get_arr_uint32",
            "name": "负数输入",
        },
        {
            "func": "test_set_arr_uint32", "param":
            [
                {"type": "int64", "value": 42949672951},
                {"type": "uint32", "value": 111},
                {"type": "uint32", "value": 111}
            ],
            "notevent": 1,
            "execpt": 4294967295,
            "call_func": "test_get_arr_uint32",
            "name": "正数溢出输入",
        },
        {
            "func": "test_set_arr_uint32", "param":
            [
                {"type": "char", "value": "mynameis"},
                {"type": "uint32", "value": 1},
                {"type": "uint32", "value": 1}
            ],
            "notevent": 1,
            "execpt": 4294967295,
            "call_func": "test_get_arr_uint32",
            "name": "字符串输入",
        },
        # int64 ###################
        {
            "func": "test_set_arr_int64", "param":
            [
                {"type": "int64", "value": 1000},
                {"type": "int64", "value": 1000},
                {"type": "int64", "value": 1000}
            ],
            "execpt": 1000,
            "call_func": "test_get_arr_int64",
            "name": "正常输入",
        },
        {
            "func": "test_set_arr_int64", "param":
            [
                {"type": "int64", "value": 0},
                {"type": "int64", "value": 11111},
                {"type": "int64", "value": 11111}
            ],
            "execpt": 0,
            "call_func": "test_get_arr_int64",
            "name": "正常输入0",
        },
        {
            "func": "test_set_arr_int64", "param":
            [
                {"type": "int64", "value": -1},
                {"type": "int64", "value": 11111},
                {"type": "int64", "value": 11111}
            ],
            "execpt": -1,
            "call_func": "test_get_arr_int64",
            "name": "负数输入",
        },
        {
            "func": "test_set_arr_int64", "param":
            [
                {"type": "int64", "value": -9223372036854775808},
                {"type": "int64", "value": 11111111},
                {"type": "int64", "value": 111111111}
            ],
            "execpt": -9223372036854775808,
            "call_func": "test_get_arr_int64",
            "name": "负数最小输入",
        },
        {
            "func": "test_set_arr_int64", "param":
            [
                {"type": "int64", "value": 9223372036854775807},
                {"type": "int64", "value": 922337203685477580},
                {"type": "int64", "value": 9223372036854775}
            ],
            "execpt": 9223372036854775807,
            "call_func": "test_get_arr_int64",
            "name": "正数最大输入",
        },
        {
            "func": "test_set_arr_int64", "param":
            [
                {"type": "int128", "value": -9223372036854775809},
                {"type": "int64", "value": 11111111},
                {"type": "int64", "value": 1111111}
            ],
            "notevent": 1,
            "execpt": 9223372036854775807,
            "call_func": "test_get_arr_int64",
            "name": "负数溢出输入",
        },
        {
            "func": "test_set_arr_int64", "param":
            [
                {"type": "int128", "value": 9223372036854775809},
                {"type": "int64", "value": 11111111111},
                {"type": "int64", "value": 11111111111}
            ],
            "notevent": 1,
            "execpt": 9223372036854775807,
            "call_func": "test_get_arr_int64",
            "name": "正数溢出输入",
        },
        {
            "func": "test_set_arr_int64", "param":
            [
                {"type": "char", "value": "asd"},
                {"type": "int64", "value": 1},
                {"type": "int64", "value": 1}
            ],
            "notevent": 1,
            "execpt": 9223372036854775807,
            "call_func": "test_get_arr_int64",
            "name": "字符串输入",
        },
        # uint64#############################
        {
            "func": "test_set_arr_uint64", "param":
            [
                {"type": "uint64", "value": 32767},
                {"type": "uint64", "value": 32767},
                {"type": "uint64", "value": 32767}
            ],
            "execpt": 32767,
            "call_func": "test_get_arr_uint64",
            "name": "正常输入",
        },
        {
            "func": "test_set_arr_uint64", "param":
            [
                {"type": "uint64", "value": 0},
                {"type": "uint64", "value": 1},
                {"type": "uint64", "value": 1}
            ],
            "execpt": 0,
            "call_func": "test_get_arr_uint64",
            "name": "正常输入最小值",
        },
        {
            "func": "test_set_arr_uint64", "param":
            [
                {"type": "uint128", "value": 18446744073709551615},
                {"type": "uint64", "value": 111111111},
                {"type": "uint64", "value": 111111111}
            ],
            "execpt": 18446744073709551615,
            "call_func": "test_get_arr_uint64",
            "name": "正常输入最大值",
        },
        {
            "func": "test_set_arr_uint64", "param":
            [
                {"type": "int16", "value": -1},
                {"type": "uint64", "value": 1},
                {"type": "uint64", "value": 1}
            ],
            "notevent": 1,
            "execpt": 18446744073709551615,
            "call_func": "test_get_arr_uint64",
            "name": "负数输入",
        },
        {
            "func": "test_set_arr_uint64", "param":
            [
                {"type": "uint128", "value": 184467440737095516151},
                {"type": "uint64", "value": 111},
                {"type": "uint64", "value": 111}
            ],
            "notevent": 1,
            "execpt": 18446744073709551615,
            "call_func": "test_get_arr_uint64",
            "name": "正数溢出输入",
        },
        {
            "func": "test_set_arr_uint64", "param":
            [
                {"type": "char", "value": "mynameis"},
                {"type": "uint64", "value": 1},
                {"type": "uint64", "value": 1}
            ],
            "notevent": 1,
            "execpt": 18446744073709551615,
            "call_func": "test_get_arr_uint64",
            "name": "字符串输入",
        },
        {
            "func": "test_set_arr_uint64", "param":
            [
                {"type": "uint64", "value": 10},
                {"type": "uint64", "value": 1},
            ],
            "noevent": "fail",
            "execpt": 18446744073709551615,
            "call_func": "test_get_arr_uint64",
            "name": "arr参数数量不足输入",
        },
        # stack double ###################
        {
            "func": "test_set_stack_double", "param":
            [
                {"type": "double", "value": 10},
                {"type": "double", "value": 10},
                {"type": "double", "value": 10}
            ],
            "execpt": 10.0,
            "call_func": "test_get_stack_double",
            "name": "正常输入",
        },
        {
            "func": "test_set_stack_double", "param":
            [
                {"type": "char", "value": "dhsjahdj"},
                {"type": "double", "value": 10},
                {"type": "double", "value": 10}
            ],
            "notevent": 1,
            "execpt": 10.0,
            "call_func": "test_get_stack_double",
            "name": "非法输入",
        },
        {
            "func": "test_set_stack_double", "param":
            [
                {"type": "double", "value": 10},
                {"type": "double", "value": 10},
            ],
            "noevent": 1,
            "execpt": 10.0,
            "call_func": "test_get_stack_double",
            "name": "stack参数数量不足输入",
        },
        # queue double ###################
        {
            "func": "test_set_queue_double", "param":
            [
                {"type": "double", "value": 10},
                {"type": "double", "value": 10},
                {"type": "double", "value": 10}
            ],
            "execpt": 10.0,
            "call_func": "test_get_queue_double",
            "name": "正常输入",
        },
        {
            "func": "test_set_queue_double", "param":
            [
                {"type": "char", "value": "dhsjahdj"},
                {"type": "double", "value": 10},
                {"type": "double", "value": 10}
            ],
            "notevent": 1,
            "execpt": 10.0,
            "call_func": "test_get_queue_double",
            "name": "非法输入",
        },
        {
            "func": "test_set_queue_double", "param":
            [
                {"type": "double", "value": 10},
                {"type": "double", "value": 10},
            ],
            "noevent": 1,
            "execpt": 10.0,
            "call_func": "test_get_queue_double",
            "name": "queue参数数量不足输入",
        },
        # map char ###################
        {
            "func": "test_set_map_char", "param":
            [
                {"type": "char", "value": "sdjksajdkasjkdadsadasd"},
                {"type": "char", "value": "sdasdasdasdsadasda"},
                {"type": "char", "value": "sdasdadasd"}
            ],
            "execpt": "sdjksajdkasjkdadsadasd",
            "call_func": "test_get_map_char",
            "name": "正常输入",
        },
        {
            "func": "test_set_map_char", "param":
            [
                {"type": "char", "value": "dhsjahdj"},
                {"type": "int8", "value": 10},
                {"type": "double", "value": 10}
            ],
            "notevent": 1,
            "execpt": "sdjksajdkasjkdadsadasd",
            "call_func": "test_get_map_char",
            "name": "非法输入",
        },
        {
            "func": "test_set_map_char", "param":
            [
                {"type": "char", "value": "sdsadasd"},
                {"type": "char", "value": "sdasdasdas"},
            ],
            "noevent": 1,
            "execpt": "sdjksajdkasjkdadsadasd",
            "call_func": "test_get_map_char",
            "name": "map参数数量不足输入",
        },
    ],
}
