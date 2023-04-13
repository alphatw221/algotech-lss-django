from django.utils import translation
from django.utils.translation import ugettext as _
from api import models

import xlsxwriter
import io

import pandas

class FieldMapper():

    def __init__(self, field_name='', title='', i18n_key=None, width=None, i18n_text=None, first_only=False, title_key=None, data_key=None, **kwargs):
        self.field_name = field_name
        self.title = title
        self._width = width
        self.i18n_key = i18n_key
        self.i18n_text = i18n_text
        self.first_only = first_only

        self.title_key = title_key
        self.data_key = data_key

        self.kwargs = kwargs
        
    def get_field_data(self,object):
        return object.get(self.field_name)

    @property
    def width(self):
        if self._width:
            return self._width
        return len(self.title)+2


class AdditionalFieldMapper():

    def __init__(self, title='', title_field_name='', title_key=None, indicator_key='', data_field_name='', data_key=None, **kwargs):
        self.title = title
        self.title_field_name = title_field_name
        self.title_key = title_key
        self.indicator_key = indicator_key
        self.data_field_name = data_field_name
        self.data_key = data_key

        self.kwargs = kwargs
    
    def get_title(self, object):

        if self.title_field_name:
            return self.title + f'({object.get(self.title_field_name)})'
        return self.title
    
    def get_field_data(self,object):
        return int(bool(object.get(self.data_field_name))), object.get(self.data_field_name)


class JSXlsxProcessor():

    

    def __init__(self, field_mappers:list=[], iterable_objects=[], reference_key = 'id',lang='en', additional_field_mappers:list=[]) -> None:
        self.field_mappers = field_mappers
        self.additional_field_mappers = additional_field_mappers
        self.iterable_objects = iterable_objects
        self.lang = lang

        self.column_settings = []
        self.header = []
        self.display_header = {}
        self.data = []
        self.reference_key = reference_key

    def __generate_header(self):

        for field_mapper in self.field_mappers:
            self.column_settings.append({"width":field_mapper.width})
            self.header.append(field_mapper.field_name)
            self.display_header[field_mapper.field_name] = _(field_mapper.i18n_key) if field_mapper.i18n_key else field_mapper.title

    def __generate_data(self):
        reference = None
        last_object = None
        for object in  self.iterable_objects:
            last_object = object
            same_object = reference==object.get(self.reference_key) if reference else False
            if reference and not same_object:

                for additional_field_mapper in self.additional_field_mappers:
                    row = {}

                    row[additional_field_mapper.title_key] = additional_field_mapper.get_title(object)
                    indicator, field_data = additional_field_mapper.get_field_data(object)

                    if additional_field_mapper.indicator_key:
                        row[additional_field_mapper.indicator_key] = indicator
                    row[additional_field_mapper.data_key] = field_data
                    self.data.append(row)

            reference = object.get(self.reference_key)

            row = {}
            for field_mapper in self.field_mappers:
                row[field_mapper.field_name] = '' if (same_object and field_mapper.first_only) else field_mapper.get_field_data(object)
            self.data.append(row)


        if last_object:
            for additional_field_mapper in self.additional_field_mappers:
                row = {}

                row[additional_field_mapper.title_key] = additional_field_mapper.get_title(last_object)
                indicator, field_data = additional_field_mapper.get_field_data(last_object)

                if additional_field_mapper.indicator_key:
                    row[additional_field_mapper.indicator_key] = indicator
                row[additional_field_mapper.data_key] = field_data
                self.data.append(row)

    def generate_json(self):
        with translation.override(self.lang):
            self.__generate_header()
            self.__generate_data()
        json = {'header':self.header, 'display_header':self.display_header, 'data':self.data, 'column_settings':self.column_settings}

        return json

    # @classmethod
    # def file_to_json(cls, file, sheet_name):
    #     excel_data_df = pandas.read_excel(io.BytesIO(file.read()), sheet_name=sheet_name)
    #     return excel_data_df.to_json()


# class XlsxImportProcessor():

#     def __init__(self) -> None:
#         pass

#     def __to_json(self, file, sheet_name=None):
        
#         excel_data_df = pandas.read_excel(io.BytesIO(file.read()), sheet_name=sheet_name)
#         json_str = excel_data_df.to_json()
#         return json_str

#     def process(self, file, sheet_name=None):
#         print(self.__to_json(file, sheet_name))

class XlsxHelper():
    row=0
    col=0
    @classmethod
    def _next_row(cls):
        cls.row+=1
    @classmethod
    def _next_column(cls):
        cls.col+=1
    @classmethod
    def _skip_row(cls,num):
        cls.row+=num
    @classmethod
    def _skip_column(cls,num):
        cls.col+=num

    @classmethod
    def _reset_row(cls):
        cls.row=0
    @classmethod
    def _reset_column(cls):
        cls.col=0

# class OrderReport(XlsxHelper):

#     columns=[
#             FieldMapper('id','ID', i18n_key='REPORT/COLUMN_TITLE/ID', i18n_text=_('REPORT/COLUMN_TITLE/ID')),
#             DateTimeMapper('created_at', 'Order Date', i18n_key='REPORT/COLUMN_TITLE/ORDER_DATE', i18n_text=_('REPORT/COLUMN_TITLE/ORDER_DATE')),
#             FieldMapper('platform', 'Platform', i18n_key='REPORT/COLUMN_TITLE/PLATFORM', i18n_text=_('REPORT/COLUMN_TITLE/PLATFORM')),
#             FieldMapper('customer_name', 'Customer Name', i18n_key='REPORT/COLUMN_TITLE/CUSTOMER_NAME', i18n_text=_('REPORT/COLUMN_TITLE/CUSTOMER_NAME')),
#             ShippingNameMapper('shipping_name', 'Shipping Name', i18n_key='REPORT/COLUMN_TITLE/SHIPPING_NAME', i18n_text=_('REPORT/COLUMN_TITLE/SHIPPING_NAME')),
#             FieldMapper('shipping_phone', 'Shipping Phone', i18n_key='REPORT/COLUMN_TITLE/SHIPPING_PHONE', i18n_text=_('REPORT/COLUMN_TITLE/SHIPPING_PHONE')),
#             FieldMapper('shipping_email', 'E-mail', i18n_key='REPORT/COLUMN_TITLE/EMAIL', i18n_text=_('REPORT/COLUMN_TITLE/EMAIL')),
#             ShippingMethodMapper('shipping_method', 'Shipping Method', i18n_key='REPORT/COLUMN_TITLE/SHIPPING_METHOD', i18n_text=_('REPORT/COLUMN_TITLE/SHIPPING_METHOD')),
#             ShippingOptionMapper('shipping_option', 'Shipping Option', i18n_key='REPORT/COLUMN_TITLE/SHIPPING_OPTION', i18n_text=_('REPORT/COLUMN_TITLE/SHIPPING_OPTION')),
#             DeliveryInfonMapper('shipping_address_1', 'Shipping Address 1', i18n_key='REPORT/COLUMN_TITLE/SHIPPING_ADDRESS_1', i18n_text=_('REPORT/COLUMN_TITLE/SHIPPING_ADDRESS_1')),
#             DeliveryInfonMapper('shipping_location', 'Location', i18n_key='REPORT/COLUMN_TITLE/LOCATION', i18n_text=_('REPORT/COLUMN_TITLE/LOCATION')),
#             DeliveryInfonMapper('shipping_region', 'Region', i18n_key='REPORT/COLUMN_TITLE/REGION', i18n_text=_('REPORT/COLUMN_TITLE/REGION')),
#             DeliveryInfonMapper('shipping_postcode', 'Postcode', i18n_key='REPORT/COLUMN_TITLE/POSTCODE', i18n_text=_('REPORT/COLUMN_TITLE/POSTCODE')),
#             PickupStoreMapper('pick_up_store', 'Pick up Store', i18n_key='REPORT/COLUMN_TITLE/PICK_UP_STORE', i18n_text=_('REPORT/COLUMN_TITLE/PICK_UP_STORE')),
#             PickupAddressMapper('pickup_address', 'Pick up Address', i18n_key='REPORT/COLUMN_TITLE/PICK_UP_ADDRESS', i18n_text=_('REPORT/COLUMN_TITLE/PICK_UP_ADDRESS')),
#             FieldMapper('shipping_remark', 'Remark', i18n_key='REPORT/COLUMN_TITLE/REMARK', i18n_text=_('REPORT/COLUMN_TITLE/REMARK')),
#             PaymentMethodMapper('payment_method', 'Payment Method', i18n_key='REPORT/COLUMN_TITLE/PAYMENT_METHOD', i18n_text=_('REPORT/COLUMN_TITLE/PAYMENT_METHOD')),
#             FieldMapper('status', 'Payment Status', i18n_key='REPORT/COLUMN_TITLE/PAYMENT_STATUS', i18n_text=_('REPORT/COLUMN_TITLE/PAYMENT_STATUS')),
#             LastFiveDigitMapper('last_five_digit', 'Payment Record', i18n_key='REPORT/COLUMN_TITLE/PAYMENT_RECORD', i18n_text=_('REPORT/COLUMN_TITLE/PAYMENT_RECORD')),
#             TotalMapper('total', 'Total', i18n_key='REPORT/COLUMN_TITLE/TOTAL', i18n_text=_('REPORT/COLUMN_TITLE/TOTAL')),
#         ]

#     @classmethod
#     def create(cls, campaign, lang='en'):
#         buffer = io.BytesIO()
        
#         workbook = xlsxwriter.Workbook(buffer,{'in_memory': True} )
#         worksheet = workbook.add_worksheet()
#         header_format = workbook.add_format({
#             'bold': True,
#             'bg_color': '#F7F7F7',
#             'color': 'black',
#             'align': 'center',
#             'valign': 'top',
#             'border': 1
#         })
#         title_format = workbook.add_format({
#             'align': 'center',
#             'bold': True,
#             'font_size': 18,
#             'border': 1
#         })
#         info_format = workbook.add_format({
#             'align': 'center',
#             'bold': True,
#             'font_size': 13,
#             'border': 1
#         })
        
#         campaign_products_count = campaign.products.count()
#         with translation.override(lang):
#             report_title = campaign.title + ' ' + _('REPORT/SECTION_TITLE/TITLE')
#             worksheet.merge_range(cls.row, 0, cls.row, len(cls.columns) + campaign_products_count - 1, report_title, title_format)
#             cls._next_row()
#             worksheet.merge_range(cls.row, 0, cls.row, 6, _('REPORT/SECTION_TITLE/CONTACT_INFO'), info_format)
#             worksheet.merge_range(cls.row, 7, cls.row, 15, _('REPORT/SECTION_TITLE/DELIVERY_INFO'), info_format)
#             worksheet.merge_range(cls.row, 16, cls.row, 19, _('PAYMENT_INFO'), info_format)
#             worksheet.merge_range(cls.row, 20, cls.row, 20 + campaign_products_count - 1, _('REPORT/SECTION_TITLE/ORDER_INFO'), info_format)
#         cls._next_row()
#         cls._reset_column()
        
#         for column in cls.columns:
#             with translation.override(lang):
#                 print(lang)
#                 print(column.i18n_key)
#                 print(_(column.i18n_key))
#                 worksheet.write(cls.row, cls.col, _(column.i18n_key), header_format)
#             worksheet.set_column(cls.col, cls.col, column.width)
#             cls._next_column()

#         product_column_dict = {}
#         for campaign_product in campaign.products.all():
#             worksheet.write(cls.row, cls.col, campaign_product.name, header_format)
#             product_column_dict[str(campaign_product.id)] = cls.col
#             cls._next_column()
#         cls._next_row()
#         cls._reset_column()

#         # orders = campaign.orders.order_by('status').all()
#         # # pre_orders = campaign.pre_orders.exclude(products__in={}).all()

#         # all_orders = list(orders)+list(pre_orders)
#         for order in campaign.orders.order_by('status').all():
#             for column in cls.columns:
#                 if column.field_name == 'total':
#                     worksheet.write(cls.row, cls.col, column.mapping(order, campaign.decimal_places))    
#                 else:
#                     worksheet.write(cls.row, cls.col, column.mapping(order))
#                 cls._next_column()

#             for campaing_product_id_str, qty in order.products.items():
#                 print(qty)
#                 worksheet.write(cls.row, product_column_dict[campaing_product_id_str], qty)
#             cls._next_row()
#             cls._reset_column()
#         cls._reset_row()

#         workbook.close()
#         buffer.seek(0)
#         return buffer
