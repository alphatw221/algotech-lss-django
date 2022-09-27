import database
from django.contrib.auth.models import User as AuthUser


class UnitTestHelper:

    @classmethod
    def create_test_data(cls, collections_data:dict={}):

        kwargs = {}
        for collection_name, collections_data in collections_data.items():

            if collection_name=='auth_user':
                kwargs = cls.__create_auth_user(collections_data, **kwargs)
                continue
               
            kwargs = cls.__create_collection(collection_name, collections_data, **kwargs)
        print(kwargs)
        return kwargs

    @staticmethod
    def __create_collection(collection_name:str, collections_data, **kwargs):

        class_name = "".join([word.capitalize() for word in collection_name.split('_')])
        collection_class = getattr(getattr(database.lss, collection_name), class_name)

        # print(kwargs)
        # print(collections_data)
        relation_data = {k: kwargs[k] for k in collection_class.template.keys() & kwargs.keys() } 

        # print(relation_data)
        collections_data.update(relation_data)
        # print(collections_data)

        document_object = collection_class.create_object(**collections_data)
        kwargs[f'{collection_name}_id']=document_object.id
        kwargs[f'{collection_name}_oid']=str(document_object._id)
        return kwargs

    @staticmethod
    def __create_auth_user(collections_data, **kwargs):
        auth_user = AuthUser.objects.create_user(**collections_data)
        kwargs['auth_user_id']=auth_user.id
        return kwargs