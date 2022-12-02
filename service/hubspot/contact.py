from ._hubspot import client
from hubspot.crm.contacts import SimplePublicObjectInput, ApiException

def update(contact_id, **kwargs):
    try:
        simple_public_object_input = SimplePublicObjectInput(properties=kwargs)
        client.crm.contacts.basic_api.update(contact_id=contact_id, simple_public_object_input=simple_public_object_input)
    except ApiException as e:
        print("Exception when calling basic_api->update: %s\n" % e)


def create(email, first_name, last_name, **kwargs):
    try:
        kwargs.update({"email":email,"first_name":first_name, "last_name":last_name})
        simple_public_object_input = SimplePublicObjectInput(properties=kwargs)
        client.crm.contacts.basic_api.create(simple_public_object_input=simple_public_object_input)
    except ApiException as e:
        print("Exception when calling basic_api->create: %s\n" % e)