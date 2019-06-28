import json
import logging
import os
import smtplib
import sys
import time
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

from deploy.deploy import AutoDeployPlaton
from common import log
from common.load_file import get_node_list
from common.connect import connect_web3
from common.abspath import abspath

class EmailInfo:
    from_addr = "sz-testing@juzix.net"
    # to_addr = ["liaoxiaoming@juzix.net", "lvxiaoyi@juzix.net",
    #            "jianghaitao@juzix.net", "liuxing@juzix.net", "fuzhijing@juzix.net"]
    to_addr = ["liaoxiaoming@juzix.net"]
    password = "Juzhen123!"
    smtp_server = "smtp.exmail.qq.com"
    header = "D网稳定性测试监控汇报"


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def send_email(email_info, msg):
    from_addr = email_info.from_addr
    password = email_info.password
    to_addr = email_info.to_addr
    smtp_server = email_info.smtp_server
    msg = MIMEText(msg, 'plain', 'utf-8')
    msg['From'] = _format_addr('dark_test <%s>' % from_addr)
    msg['To'] = ",".join(to_addr)
    msg['Subject'] = Header(email_info.header, 'utf-8').encode()
    print(smtp_server)
    server = smtplib.SMTP_SSL(host=smtp_server)
    server.connect(smtp_server, 465)
    # server.set_debuglevel(1)
    server.login(from_addr, password)
    server.sendmail(from_addr, to_addr, msg.as_string())
    server.quit()

def monitor(node_yml):
    auto = AutoDeployPlaton()
    collusion, nocollusion = get_node_list(node_yml)
    node_list = collusion + nocollusion
    old_block = [0 * i for i in range(len(collusion))]
    t = 0
    while True:
        time.sleep(120)
        t += 120
        block_list = []
        url_list = []
        for node in node_list:
            try:
                w3 = connect_web3(node["url"])
                if not w3.isConnected():
                    raise Exception("有节点被关闭了")
                block = w3.eth.blockNumber
                block_list.append(block)
                url_list.append(node["url"])

            except:
                close_msg = "节点:{}:{}无法连接\n".format(
                    node["host"], node["port"])
                log.warning(close_msg)
        msg = build_msg(url_list, block_list, old_block)
        if max(block_list) - min(block_list) >= 100:
            log.error("区块差距过大")
            auto.kill_of_yaml(node_yml)
            send_to_gap(block_list, msg, node_yml)
        if max(block_list) - min(old_block) == 0:
            log.error("不出块了")
            auto.kill_of_yaml(node_yml)
            send_to_block(msg, node_yml)
        if t >= 21600:
            t = 0
            send_email(EmailInfo, msg)
        old_block = block_list


def build_msg(url_list, block_list, old_block):
    block_dict = dict(zip(url_list, block_list))
    msg = "以下是各节点最新出块情况\n"
    old_msg = "各节点120s前块高为{}\n".format(old_block)
    for url in url_list:
        b = block_dict[url]
        msg += "节点：{}，块高：{}\n".format(url, b)
    msg = msg + "\n" + old_msg
    return msg


def send_to_gap(block_list, msg, node_yml):
    error = "出现问题原因:区块差距过大\n\n"
    error += "最高块高为：{},".format(max(block_list))
    error += "最低块高为：{}\n".format(min(block_list))
    msg = error + msg
    EmailInfo.header = "D网稳定性测试监控汇报-块高差距过大"
    send_email(EmailInfo, msg)
    stop(node_yml)

def send_to_block(msg,node_yml):
    error = "出现问题原因：已经120s各节点块高没有增长\n\n"
    msg = error + msg
    EmailInfo.header = "D网稳定性测试监控汇报-不出块"
    send_email(EmailInfo, msg)
    stop(node_yml)

def stop(node_yml):
    auto = AutoDeployPlaton()
    auto.stop_of_yml(node_yml)
    raise Exception("出现报错，监控停止")

if __name__ == "__main__":
    try:
        node_yml = sys.argv[1]
    except:
        node_yml = abspath("./deploy/node/cbft_25_node.yml")
    monitor(node_yml)
