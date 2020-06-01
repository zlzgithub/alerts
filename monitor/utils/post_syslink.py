#!/usr/bin/python2
# coding=utf8
import os
import sys
import json
import requests
import logging

reload(sys)
sys.setdefaultencoding('utf-8')
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s (%(filename)s:L%(lineno)d)',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='/tmp/post_syslink.log',
                    filemode='a')
logger = logging.getLogger(__name__)
token = 'xxxxxx'
server_ip = '192.168.100.150'
server_name = 'alerts888.yhglobal.cn'
headers = {"Host": server_name}
url = "http://{}/monitor/received/syslink/info/".format(server_ip)
url = "http://{}/monitor/received/syslink/data/".format(server_ip)


def post_data(payload):
    try:
        logger.info("payload is: {}".format(payload))
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        logger.info("r.status_code is: {}".format(r.status_code))
        if r.text:
            logger.info(r.text)
            print("{} {}".format(r.status_code, r.text))
        else:
            logger.info("Server return http status code: {0}".format(r.status_code))
    except Exception as msg:
        logger.info(msg)


if __name__ == '__main__':
    try:
        para01 = sys.argv[1]
        if '-f' == para01:
            para02 = sys.argv[2]
            if not os.path.exists(para02):
                print("No such file: {}".format(para02))
                exit(1)
            else:
                with open(para02, 'r') as f:
                    para01 = f.read()
        try:
            data = json.loads(para01)
        except:
            exit(2)

        payload = {
            "token": token
        }
        if isinstance(data, list):
            payload["data"] = data
        else:
            payload.update(data)
        print(payload)
        post_data(payload)
    except Exception as e:
        print(str(e))
