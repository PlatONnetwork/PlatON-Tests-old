# -*- coding:utf-8 -*-

"""
@Author: @Author
@Date: @Date @Eime
@LastEditors: @Author
@LastEditTime: @Date @Eime
@Description:
"""


class OperateVersion:
    def __init__(self,rpc_link,flag):
        self.rpc_link=rpc_link
        self.flag=flag

    def get_version(self):
        '''
        获取版本号，不传入flag，为获取链上版本号，例：链上版本号为0.7.0
        flag = 1（获取小于链上主版号） 0.6.0
        flag = 2 (获取等于链上主版本号，小版本号不等于) 0.7.1
        flag = 3 (获取大于链上主版本号) 0.8.0
        :param flag:
        :return:
        '''

        msg = self.rpc_link.getActiveVersion()
        version = int(msg.get('Data'))

        #返回链上版本号
        if not self.flag:
            new_version = version

        elif self.flag==1:
            ver_byte = (version).to_bytes(length=4, byteorder='big', signed=False)
            ver0 = ver_byte[0]
            ver1 = ver_byte[1]
            ver2 = ver_byte[2]
            ver3 = ver_byte[3]
            new_ver3 = (ver2 - 1).to_bytes(length=1, byteorder='big', signed=False)
            new_version_byte = ver_byte[0:1] + new_ver3 + ver_byte[3:]
            new_version = int.from_bytes(new_version_byte, byteorder='big', signed=False)

        elif self.flag==2:
            ver_byte = (version).to_bytes(length=4, byteorder='big', signed=False)
            ver0 = ver_byte[0]
            ver1 = ver_byte[1]
            ver2 = ver_byte[2]
            ver3 = ver_byte[3]
            new_ver3 = (ver3 + 1).to_bytes(length=1, byteorder='big', signed=False)
            print(ver_byte[0:2])
            print(new_ver3)
            new_version_byte = ver_byte[0:3] + new_ver3
            new_version = int.from_bytes(new_version_byte, byteorder='big', signed=False)

        elif self.flag==3:
            ver_byte = (version).to_bytes(length=4, byteorder='big', signed=False)
            ver0 = ver_byte[0]
            ver1 = ver_byte[1]
            ver2 = ver_byte[2]
            ver3 = ver_byte[3]
            new_ver2 = (ver2 + 1).to_bytes(length=1, byteorder='big', signed=False)
            new_version_byte = ver_byte[0:1] + new_ver2 + ver_byte[3:]
            new_version = int.from_bytes(new_version_byte, byteorder='big', signed=False)
        else:
            pass
        return new_version
