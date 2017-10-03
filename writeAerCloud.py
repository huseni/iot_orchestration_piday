#!/usr/bin/env python

########################################
#                                      #
#  POST SMS DATA ONTO AIRCLOUD         #
#                                      #
########################################

import json
import sys
import requests
from pprint import pprint


def post_to_aercloud(timestamp=None, message="", status="FAIL"):
    """
    To post the SMS data on to AERCLOUD
    """
    data={
        "timestamp" : "%s" % (timestamp),
        "messageBody" : "%s" % (str(message)),
        "messageDirection" : "To",
        "deviceId" : "231242143443",
        "status" : "%s" %(status)
    }

    dataAsJSON = json.dumps(data)
    headers = {  "Content-type" : "application/json"  }
    response = requests.post("https://api.aercloud.aeris.com/v1/1/scls/353147040226062/containers/team8IoTData/contentInstances?apiKey=27f10c82-2f05-40d5-81f6-572e3c44c175", data=dataAsJSON, headers=headers )
    print(response)
    if response:  
        if response.status_code == 200:
            print("*********** Successfully posted data into Aercloud ***************")
            print("************ Content ****************")
            pprint(response.content)
            print("*********** Headers ******************")
            pprint(response.headers)



if __name__ == '__main__':
    post_to_aercloud(timestamp=None, message="", status="FAIL")