from struct import pack

from data.basic import func
from utils.platon_lib import encoder


def handle(contract_address):
    for k, v in contract_address.items():
        for f in func[k]:
            f["contract_name"] = k
            f["contract_address"] = v


def handle_param(data):
    """
    wohenshuai
    """
    result = []
    if isinstance(data, list):
        for d in data:
            result.append(encode(d))
    elif isinstance(data, dict):
        result.append(encode(data))
    else:
        raise Exception("""参数合适不正确：
        example:
        [
            {"type": "uint32", "value": ""},
            {"type": "uint32", "value": ""},
            {"type": "uint32", "value": ""}
        ],
        or 
        {"type": "uint32", "value": ""}
        """)
    return result


def encode(data_dict):
    if "int" in data_dict["type"]:
        if data_dict["type"] == "int":
            data_dict["type"] = "int8"
        encode_result = encoder.encode_int(data_dict["type"], data_dict["value"])
    elif data_dict["type"] == "double":
        encode_result = pack('f', data_dict["value"])
    elif data_dict["type"] == "long":
        encode_result = encoder.encode_int("int64", data_dict["value"])
    elif data_dict["type"] == "bool":
        encode_result = encoder.encode_boolean(data_dict["value"])
    elif data_dict["type"] == "char":
        encode_result = encoder.encode_string(data_dict["value"])
    else:
        raise Exception("""参数类型不正确!
        类型必须是int,int8,uint8,int16,uint16,int32,uint32,int64,uint64,double,long,bool,char
        """)
    return encode_result
