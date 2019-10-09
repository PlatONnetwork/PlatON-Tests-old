import threading


def run_thread(data: list, func, *args):
    """
    多线程运行封装
    :param data: 数据列表
    :param func: 方法
    :param args: 参数
    :return:
    """
    threads = []
    i = 0
    for d in data:
        param = [p for p in args]
        param.insert(0, d)
        param = tuple(param)
        t = threading.Thread(target=func, args=param)
        t.start()
        threads.append(t)
        i += 1
    for t2 in threads:
        t2.join()
