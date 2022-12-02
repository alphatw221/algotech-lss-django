import lib
import pandas
from api import models
import io
import json

CONTENT_TYPE_XLSX = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
CONTENT_TYPE_CSV = 'text/csv'



class DefaultCustomerImportProcessor(lib.helper.import_helper.ImportProcessor):

    def __init__(self, user_subscription, size_limit_bytes=100*1024, accept_types=[CONTENT_TYPE_XLSX, CONTENT_TYPE_CSV]) -> None:

        self.user_subscription = user_subscription
        self.sheet_name = 'sheets'
        
        super().__init__(size_limit_bytes, accept_types)

    def size_not_valid(self):
        raise lib.error_handle.error.api_error.ApiVerifyError('size_invalid')


    def type_not_valid(self):
        raise lib.error_handle.error.api_error.ApiVerifyError('type_invalid')


    def file_to_data(self, file):

        if file.content_type == CONTENT_TYPE_XLSX:
            excel_data_df = pandas.read_excel(io.BytesIO(file.read()), sheet_name=self.sheet_name)
            return json.loads( excel_data_df.to_json(orient='records'))
        elif file.content_type == CONTENT_TYPE_CSV:
            excel_data_df = pandas.read_csv(io.BytesIO(file.read()))
            return json.loads( excel_data_df.to_json(orient='records'))

    def save_data(self, data):
        pass
