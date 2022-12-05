from attr import attributes
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from ._sendinblue import api_client

def create(email, first_name=None, last_name=None, list_ids=None):
    

    try:
        api_instance = sib_api_v3_sdk.ContactsApi(api_client)
        create_contact = sib_api_v3_sdk.CreateContact(email=email, attributes={"FIRSTNAME":first_name, "LASTNAME":last_name}, list_ids=list_ids if list_ids else None,)
        api_instance.create_contact(create_contact)
    except ApiException as e:
        print("Exception when calling ContactsApi->create_contact: %s\n" % e)