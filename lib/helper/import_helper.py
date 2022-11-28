import abc
class FieldMapper():

    def __init__(self, json_field, model_field, default=None, **kwargs):
        self.json_field = json_field
        self.model_field = model_field
        self.default = default
        self.kwargs = kwargs

    def get_model_data(self, object):
        return object.get(self.json_field, self.default)


class ImportProcessor():
    
    def __init__(self, size_limit_bytes=10*1024, accept_types=[]) -> None:

        self.size_limit_bytes = size_limit_bytes
        self.accept_types = accept_types

    def check_size_valid(self, file):
        if self.size_limit_bytes and getattr(file, 'size', 0) > self.size_limit_bytes:
            return self.size_not_valid()
        return True


    def check_type_valid(self, file):
        print(file.content_type)
        if self.accept_types and getattr(file, 'content_type') not in self.accept_types:
            return self.type_not_valid()
        return True

    @abc.abstractmethod
    def size_not_valid(self):
        pass

    @abc.abstractmethod
    def type_not_valid(self):
        pass

    @abc.abstractmethod
    def file_to_data(self, file):
        pass

    @abc.abstractmethod
    def save_data(self, data):
        pass


    def process(self, file):

        if not self.check_size_valid(file):
            return
        
        if not self.check_type_valid(file):
            return

        data = self.file_to_data(file)
        self.save_data(data)