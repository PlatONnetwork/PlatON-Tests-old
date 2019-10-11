from concurrent.futures.thread import ThreadPoolExecutor


def initGlobal():
    global _global_dict
    _global_dict = {}
    _global_dict["threadPoolExecutor"] = ThreadPoolExecutor(max_workers=30)


def set_value(name, value):
    _global_dict[name] = value

def get_value(name, defValue=None):
    try:
        return _global_dict[name]
    except KeyError:
        return defValue


def getThreadPoolExecutor(defValue=None):
    try:
        return _global_dict["threadPoolExecutor"]
    except KeyError:
        return defValue
