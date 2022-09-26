import database

class UnitTestHelper:

    @classmethod
    def create_test_data(cls, collections_data:dict={}):

        kwargs = {}
        for collection_name, collections_data in collections_data.items():
            kwargs = cls.__create_collection(collection_name, collections_data, **kwargs)
        return kwargs

    @staticmethod
    def __create_collection(collection_name:str, collections_data, **kwargs):

        # class_name = "".join([for ])
        collection_class = getattr(getattr(database.lss, collection_name),collection_name.capitalize())

        print(kwargs)
        print(collections_data)
        relation_data = {k: kwargs[k] for k in collection_class.template.keys() & kwargs.keys() } 

        print(relation_data)
        collections_data.update(relation_data)
        print(collections_data)

        document = collection_class.create(**collections_data)
        kwargs[f'{collection_name}_id']=document.get('id')
        return kwargs