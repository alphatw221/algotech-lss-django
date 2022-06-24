import binascii
import hashlib
import pytz
import datetime
import lib
def createHash(chargetotal,currency,storeId,sharedSecret,timezone,txndatetime):
            
    stringToHash = str(storeId) + txndatetime + str(chargetotal) + str(currency) + sharedSecret
    ascii = binascii.b2a_hex(stringToHash.encode())   
    hash_object = hashlib.sha256(ascii)
    return hash_object.hexdigest()
    
def getDateTime(timezone):
    if(timezone not in pytz.all_timezones):
        raise lib.error_handle.error.api_error.ApiVerifyError('Payment Error, Please Choose Another Payment Method')
    timezone = pytz.timezone(timezone)
    return datetime.datetime.now(timezone).strftime("%Y:%m:%d-%H:%M:%S")