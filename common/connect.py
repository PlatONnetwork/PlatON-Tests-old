'''
@Author: xiaoming
@Date: 2018-12-01 14:38:42
@LastEditors: xiaoming
@LastEditTime: 2019-01-16 10:47:19
@Description: 用于连接linux服务器或者web3
'''
import paramiko
from client_sdk_python import HTTPProvider, Web3, WebsocketProvider
from client_sdk_python.middleware import geth_poa_middleware

from common.log import log


def connect_web3(url):
    '''
    连接web3服务,增加区块查询中间件,用于实现eth_getBlockByHash,eth_getBlockByNumber等方法
    '''
    if "ws" in url:
        w3 = Web3(WebsocketProvider(url))
    else:
        w3 = Web3(HTTPProvider(url))
    w3.middleware_stack.inject(geth_poa_middleware, layer=0)
    
    return w3


def connect_linux(ip, username='root', password='Juzhen123!', port=22):
    '''
    使用账号密码连接linux服务器
    params:
        @ip:服务器ip
        @username:用户名
        @password:密码
    return:
        @ssh:ssh实例，用于执行命令 ssh.exec_command(cmd)
        @sftp:文件传输实例，用于上传下载文件 sftp.get(a,b)将a下载到b,sftp.put(a,b)把a上传到b
        @t:连接实例，用于关闭连接 t.close()
    '''
    t = paramiko.Transport((ip, port))
    t.connect(username=username, password=password)
    ssh = paramiko.SSHClient()
    ssh._transport = t
    sftp = paramiko.SFTPClient.from_transport(t)
    return ssh, sftp, t

def connect_linux_pem(ip, username, pem_path):
    '''
     使用秘钥连接linux服务器
     params:
         @ip:服务器ip
         @username:用户名
         @pem_path:秘钥路径
     return:
         @ssh:ssh实例，用于执行命令 ssh.exec_command(cmd)
         @sftp:文件传输实例，用于上传下载文件 sftp.get(a,b)将a下载到b,sftp.put(a,b)把a上传到b
         @t:连接实例，用于关闭连接 t.close()
     '''
    key = paramiko.RSAKey.from_private_key_file(pem_path)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username=username, pkey=key)
    t = ssh.get_transport()
    sftp = paramiko.SFTPClient.from_transport(t)
    return ssh, sftp, t


def run_ssh(ssh, cmd, password=None):
    try:
        stdin, stdout, _ = ssh.exec_command("source /etc/profile;%s" % cmd)
        if password:
            stdin.write(password+"\n")
        stdout_list = stdout.readlines()
        if len(stdout_list):
            log.debug(stdout_list)
    except Exception as e:
        raise e
    return stdout_list


def runCMDBySSH(ssh, cmd, password=None, password2=None, password3=None):
    try:
        log.info('execute shell cmd::: {} '.format(cmd))
        stdin, stdout, _ = ssh.exec_command("source /etc/profile;%s" % cmd)
        if password:
            stdin.write(password+"\n")
        if password2:
            stdin.write(password2+"\n")
        if password3:
            stdin.write(password3+"\n")

        stdout_list = stdout.readlines()
        if len(stdout_list):
            log.info('{}:{}'.format(cmd,stdout_list) )
    except Exception as e:
        raise e
    return stdout_list
