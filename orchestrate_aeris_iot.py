#!/usr/bin/env python3
##########################################################################################################################
# THIS PROGRAM IS TO ORCHESTRATE THE END-TO-END SMS SENT THROUGH AERFRAME AND STORE THE RESPONSE RECEIVED ONTO AERCLOUD  #
#                                                                                                                        # 
#                                                                                                                        #
##########################################################################################################################

# STANDARD LIB
import time
from pprint import pprint
import os
import sys
import http.server
import socketserver
import json
import urllib.request
import serial
import time
from cgi import parse_qs, escape


# USER DEFINED LIB
from writeAerframe import *
from writeAerCloud import *


# GLOBAL VARIABLE
conName = "Aeris-Test"
#ser.port = 'COM9'
#ser.port = 'COM24'
#ser.timeout = 5
#ser.baudrate = 115200

# Global handle for RAS
hras = 0
respExt="json"
# Web server Port and IP address
MyPort = 9090
MyIPAddress = '0.0.0.0'
cdmaMDN ='1847600412'

callbackHRASCon=''
callbackMSG=''
callbackRASCS=''
callbackError=''
callbackExtError=''
#getsmsResultCode = -1
deleteLatestSMSResultCode=-1
resetDeviceResultCode=-1
isDeviceAvailableResultCode=-1


class TextMessage(object):
    def __init__(self, recipient="+14254637311", message="TextMessage.content not set."):
        self.recipient = recipient
        self.content = message
        self.getsmsResultCode = 1
        self.requestTimer = 0.0
        #self.ser.port = 'COM9'
        self.requestTimeDuration = 0

    def setRecipient(self, number):
        self.recipient = number

    def setContent(self, message):
        self.content = message

    def connectPhone(self):
        self.ser = serial.Serial('/dev/gsmmodem', 460800, timeout=5)
        pprint(self.ser)
        time.sleep(1)

    def sendMessage(self):
        self.ser.write('ATZ\r')
        print("atzresponse1    "+self.ser.readline())
        print("atzresponse2    "+self.ser.readline())
        print("atzresponse3    "+self.ser.readline())
        time.sleep(1)
        self.ser.write('AT+CMGF=1\r')
        print("atcmgfresponse1   "+self.ser.readline())
        print("atcmgfresponse2   "+self.ser.readline())
        print("atcmgfresponse3   "+self.ser.readline())
        print("atcmgfresponse4   "+self.ser.readline())
        time.sleep(2)
        self.ser.write('''AT+CMGS="''' + self.recipient + '''"\r''')
        print("atcmgsresponse1   "+ self.ser.readline()) 
        print("atcmgsresponse2   "+ self.ser.readline())
        print("atcmgsresponse3   "+ self.ser.readline())
        print("atcmgsresponse4   "+ self.ser.readline())
        time.sleep(2)
        self.ser.write(self.content + "\r")
        time.sleep(1)
        self.ser.write(chr(26))
        time.sleep(1)
        data = self.ser.readline()
        print("shreponse   "+data)

    def disconnectPhone(self):
        self.ser.close()

    def read_to_return(self):
        #global requestTimer
        requestTimer = time.time()
        myReturn = ""
        counter = 0
        condition = True
        while condition:
                # loop body here
                myReturn = myReturn + self.ser.read(1).decode("ascii")
                counter = counter + 1
                if counter > 6 and myReturn[-6:] == "\r\nOK\r\n":
                        condition = False
                currTime = time.time()
                self.requestTimeDuration = currTime - requestTimer
                print("currTime:"+str(time.asctime( time.localtime(currTime))))
                print("requestTimer:"+str(time.asctime( time.localtime(requestTimer))))
                print("requestTimeDuration:"+str(self.requestTimeDuration))
                if (self.requestTimeDuration > 20) :
                        condition = False
                        myReturn = "request Timed out for reading from the Com Port"
                        return(-2,myReturn)
        # end of loop
        print ("End of read_to_return")
        return (1, myReturn)
    
    def my_set_smsFormatAsText(self):
        cmdSetCMGF = "AT+CMGF=1\r"
        cmdSetCNMI = "AT+CNMI=2\r"
        self.ser.write(cmdSetCMGF.encode("ascii","ignore"))
        cmgf = self.read_to_return()
        self.ser.write(cmdSetCNMI.encode("ascii","ignore"))
        cnmi = read_to_return()

    def my_get_smsStorageDetails(self):
        cpms = ""
        self.ser.write("AT+CPMS?\r".encode("ascii","ignore"))
        returnCode, cpms = self.read_to_return()
        if(returnCode==-2):
            return (-2,"request Timed out for reading from the Com Port")
        print("AT+CPMS? return: ", cpms)
        lhs, rhs = cpms.split("+CPMS: ")
        strCPMS = rhs
        return strCPMS
	
    def my_getlatestsmsLocation(self):
        strCPMS = self.my_get_smsStorageDetails()
        print("strCPMS:"+strCPMS)
        strCPMS=strCPMS.replace(',','\n')
        print("strCPMS1:"+strCPMS)
        resultCPMS = strCPMS.splitlines()
        print("resultCPMS :"+str(resultCPMS))
        maxMEMR = str(resultCPMS[2])
        maxMEMW = str(resultCPMS[5])
        print("maxMEMR:"+maxMEMR)
        print("maxMEMW:"+maxMEMW)
        usedrIndex = str(resultCPMS[1])
        print("usedrIndex:"+usedrIndex)
        return usedrIndex

    @staticmethod
    def generate_unix_epoc():
        """
        Generate EPOC
        """
        return calendar.timegm(time.strptime('Mar 14, 2027 @ 22:02:58 UTC', '%b %d, %Y @ %H:%M:%S UTC'))
	
    def	my_get_latestSMS(self):
	
	#global requestTimer	
        smsText=""
        usedrIndex = self.my_getlatestsmsLocation()
        smsIndex = int(usedrIndex)
        smsIndex = smsIndex-1
        print("smsIndex"+str(smsIndex))
        if(smsIndex<0):
            print("Error while processing no SMS")
            return str(smsText)
        else:
            cmdGetSMS = "AT+CMGR="+str(smsIndex)+"\r"
            print("cmdGetSMS:"+str(cmdGetSMS))
            self.ser.write(cmdGetSMS.encode("ascii","ignore"))
            myReturn = ""
            counter = 0
            condition = True
            while condition:
                myReturn = myReturn + self.ser.read(1).decode("ascii")
                counter = counter + 1
                if(myReturn.find("\r\nOK\r\n")!=-1):
                    condition = False
                self.requestTimeDuration = time.time() - self.requestTimer
                if(self.requestTimeDuration > 30) :
                    condition = False
                    myReturn = "request Timed out for reading from the Com Port"
                    return(-2,myReturn)
                myReturn=myReturn.replace("\r\nOK\r\n","")
                print("myReturn:"+str(myReturn))
                lhs, rhs =myReturn.split('+CMGR: "REC READ",')
                myReturn = str(rhs)
                lhs, rhs =myReturn.split("\n",1)
                myReturn = str(rhs)
                smsText=myReturn
                print("smsText:"+str(smsText))
                self.getsmsResultCode=1
                print("getsmsResultCode:"+str(getsmsResultCode))
                return str(smsText)



if __name__ == '__main__':
   
    status = 'FAIL'  
    # Generate EPOC
    epoc_val = generate_unix_epoc()

    print(" *********epoc value*************")
    print(epoc_val)
    print(" ********************************")	
      
    # Send SMS to AerFrame #
    post_request(epoc_val)
    
	# Wait for the SMS tobe sent from AerFrame
    time.sleep(10)   

    sms = TextMessage("+14254637311","This is the new message.")
    sms.connectPhone()

    sms.my_get_latestSMS()
    returnedMsg = sms.read_to_return()
 
    print(" **********************************************************************************************")
    pprint(returnedMsg)
    print(type(returnedMsg))
    print(" ***********************************************************************************************")
    if epoc_val in returnedMsg:
        status = "SUCCESS"
    post_to_aercloud(epoc_val, returnedMsg, status) 

    sms.disconnectPhone()
    pprint(sms.disconnectPhone())
    print ("**** Executed successfully *****")

