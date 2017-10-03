#!/usr/bin/env python

#####################################################
#                                                   #
#  THIS PROGRAM IS TO SEND SMS TO AERFRAME          #
#                                                   #  
#                                                   #
#####################################################
import json
import sys
from pprint import pprint
import calendar
import time
import requests


def generate_unix_epoc():
    """
    Generate EPOC
    """
    return calendar.timegm(time.strptime('Mar 14, 2027 @ 22:02:58 UTC', '%b %d, %Y @ %H:%M:%S UTC'))


def post_request(epoc_val):
    data = {
        "address": [
            "310170202454602"
        ],
        "senderAddress": "taf-papp",
        "outboundSMSTextMessage": {
            "message": "%s" %(epoc_val)
        } ,
        "clientCorrelator": "123456",
        "senderName": "AFTestClient"
    } 

    dataAsJSON = json.dumps(data)
    headers = {  "Content-type" : "application/json"  }
    response = requests.post("https://api.aerframe.aeris.com/smsmessaging/v2/1/outbound/taf-papp/requests?apiKey=3965e581-120d-11e2-8fb3-6362753ec2a5", data=dataAsJSON, headers=headers)
    if response:  
        if response.status_code == 201:
            print("*********** Successfully able to send SMS ***************")
            pprint(response.content)
            pprint(response.headers)
        else:
            print("Unable to send SMS through AerFrame")