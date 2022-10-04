from django.utils import translation
from django.utils.translation import ugettext as _
from api import models

import xlsxwriter
import io

class FieldMapper():
    field_name=''
    title=''
    i18n_key=None
    _width=None
    
    def __init__(self, field_name=None, title=None, i18n_key=None, width=None):
        if field_name!=None:
            self.field_name = field_name
        if title!=None:
            self.title = title
        if width!=None:
            self._width = width
        if i18n_key!=None:
            self.i18n_key = i18n_key
            
    def mapping(self,object):
        return getattr(object,self.field_name)

    @property
    def width(self):
        if self._width:
            return self._width
        return len(self.title)+2

class DateTimeMapper(FieldMapper):
    def mapping(self, object):
        return super().mapping(object).strftime("%Y-%m-%d")

class ShippingNameMapper(FieldMapper):
    def mapping(self, object):
        return  f'{object.shipping_last_name} {object.shipping_first_name}'

class CustomerNameMapper(FieldMapper):
    def mapping(self, object):
        return getattr(object, 'customer_name')

class ShippingMethodMapper(FieldMapper):
    def mapping(self, object):
        shipping_method = 'Delivery' if super().mapping(object)== models.order.order.SHIPPING_METHOD_DELIVERY else 'Pick Up'
        return shipping_method
class ShippingOptionMapper(FieldMapper):
    def mapping(self, object):
        
        shipping_option=super().mapping(object)
        shipping_option = 'Default' if shipping_option == '' else shipping_option
        return shipping_option

class DeliveryInfonMapper(FieldMapper):
    def mapping(self, object):
        shipping_method=getattr(object, 'shipping_method')
        info_data = '' if shipping_method == models.order.order.SHIPPING_METHOD_PICKUP or object.status not in ['complete', 'shipping out'] else super().mapping(object)
        return info_data

class PickupStoreMapper(FieldMapper):
    def mapping(self, object):
        shipping_method=getattr(object, 'shipping_method')
        if shipping_method == models.order.order.SHIPPING_METHOD_DELIVERY or object.status not in ['complete', 'shipping out']:
            info_data = ''
        else:
            info_data = object.campaign.meta_logistic['pickup_options'][object.shipping_option_index]['name']
        return info_data
class PickupAddressMapper(FieldMapper):
    def mapping(self, object):
        shipping_method=getattr(object, 'shipping_method')
        info_data = '' if shipping_method == models.order.order.SHIPPING_METHOD_DELIVERY or object.status not in ['complete', 'shipping out'] else super().mapping(object)
        return info_data

class PaymentMethodMapper(FieldMapper):
    def mapping(self, object):
        data = f'Direct Payment - {object.meta.get("account_mode", "")}' if object.payment_method == 'direct_payment' else super().mapping(object)
        return data
class LastFiveDigitMapper(FieldMapper):
    def mapping(self, object):
        if not object.meta.get(self.field_name, ''):
            return object.meta.get('receipt_image', '')
        return object.meta.get(self.field_name, '')
class TotalMapper(FieldMapper):
    def mapping(self, object, decimal_places):
        info_data = int(super().mapping(object)) if decimal_places == 0 else super().mapping(object)
        return info_data
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

class OrderReport(XlsxHelper):

    columns=[
            FieldMapper('id','ID', i18n_key='REPORT/COLUMN_TITLE/ID'),
            DateTimeMapper('created_at', 'Order Date', i18n_key='REPORT/COLUMN_TITLE/ORDER_DATE'),
            FieldMapper('platform', 'Platform', i18n_key='REPORT/COLUMN_TITLE/PLATFORM'),
            CustomerNameMapper('customer_name', 'Customer Name', i18n_key='REPORT/COLUMN_TITLE/CUSTOMER_NAME'),
            ShippingNameMapper('shipping_name', 'Shipping Name', i18n_key='REPORT/COLUMN_TITLE/SHIPPING_NAME'),
            FieldMapper('shipping_phone', 'Shipping Phone', i18n_key='REPORT/COLUMN_TITLE/SHIPPING_PHONE'),
            FieldMapper('shipping_email', 'E-mail', i18n_key='REPORT/COLUMN_TITLE/EMAIL'),
            ShippingMethodMapper('shipping_method', 'Shipping Method', i18n_key='REPORT/COLUMN_TITLE/SHIPPING_METHOD'),
            ShippingOptionMapper('shipping_option', 'Shipping Option', i18n_key='REPORT/COLUMN_TITLE/SHIPPING_OPTION'),
            DeliveryInfonMapper('shipping_address_1', 'Shipping Address 1', i18n_key='REPORT/COLUMN_TITLE/SHIPPING_ADDRESS_1'),
            DeliveryInfonMapper('shipping_location', 'Location', i18n_key='REPORT/COLUMN_TITLE/LOCATION'),
            DeliveryInfonMapper('shipping_region', 'Region', i18n_key='REPORT/COLUMN_TITLE/REGION'),
            DeliveryInfonMapper('shipping_postcode', 'Postcode', i18n_key='REPORT/COLUMN_TITLE/POSTCODE'),
            PickupStoreMapper('pick_up_store', 'Pick up Store', i18n_key='REPORT/COLUMN_TITLE/PICK_UP_STORE'),
            PickupAddressMapper('pickup_address', 'Pick up Address', i18n_key='REPORT/COLUMN_TITLE/PICK_UP_ADDRESS'),
            FieldMapper('shipping_remark', 'Remark', i18n_key='REPORT/COLUMN_TITLE/REMARK'),
            PaymentMethodMapper('payment_method', 'Payment Method', i18n_key='REPORT/COLUMN_TITLE/PAYMENT_METHOD'),
            FieldMapper('status', 'Payment Status', i18n_key='REPORT/COLUMN_TITLE/PAYMENT_STATUS'),
            LastFiveDigitMapper('last_five_digit', 'Payment Record', i18n_key='REPORT/COLUMN_TITLE/PAYMENT_RECORD'),
            TotalMapper('total', 'Total', i18n_key='REPORT/COLUMN_TITLE/TOTAL'),
        ]

    @classmethod
    def create(cls, campaign, lang='en'):
        buffer = io.BytesIO()
        
        workbook = xlsxwriter.Workbook(buffer,{'in_memory': True} )
        worksheet = workbook.add_worksheet()
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#F7F7F7',
            'color': 'black',
            'align': 'center',
            'valign': 'top',
            'border': 1
        })
        title_format = workbook.add_format({
            'align': 'center',
            'bold': True,
            'font_size': 18,
            'border': 1
        })
        info_format = workbook.add_format({
            'align': 'center',
            'bold': True,
            'font_size': 13,
            'border': 1
        })
        
        campaign_products_count = campaign.products.count()
        with translation.override(lang):
            report_title = campaign.title + ' ' + _('REPORT/SECTION_TITLE/TITLE')
            worksheet.merge_range(cls.row, 0, cls.row, len(cls.columns) + campaign_products_count - 1, report_title, title_format)
            cls._next_row()
            worksheet.merge_range(cls.row, 0, cls.row, 6, _('REPORT/SECTION_TITLE/CONTACT_INFO'), info_format)
            worksheet.merge_range(cls.row, 7, cls.row, 15, _('REPORT/SECTION_TITLE/DELIVERY_INFO'), info_format)
            worksheet.merge_range(cls.row, 16, cls.row, 19, _('REPORT/SECTION_TITLE/PAYMENT_INFO'), info_format)
            worksheet.merge_range(cls.row, 20, cls.row, 20 + campaign_products_count - 1, _('REPORT/SECTION_TITLE/ORDER_INFO'), info_format)
        cls._next_row()
        cls._reset_column()
        
        for column in cls.columns:
            with translation.override(lang):
                print(lang)
                print(column.i18n_key)
                print(_(column.i18n_key))
                worksheet.write(cls.row, cls.col, _(column.i18n_key), header_format)
            worksheet.set_column(cls.col, cls.col, column.width)
            cls._next_column()

        product_column_dict = {}
        for campaign_product in campaign.products.all():
            worksheet.write(cls.row, cls.col, campaign_product.name, header_format)
            product_column_dict[str(campaign_product.id)] = cls.col
            cls._next_column()
        cls._next_row()
        cls._reset_column()

        orders = campaign.orders.order_by('status').all()
        pre_orders = campaign.pre_orders.exclude(products__in={}).all()

        all_orders = list(orders)+list(pre_orders)
        for order in all_orders:
            for column in cls.columns:
                if column.field_name == 'total':
                    worksheet.write(cls.row, cls.col, column.mapping(order, campaign.decimal_places))    
                else:
                    worksheet.write(cls.row, cls.col, column.mapping(order))
                cls._next_column()

            for campaing_product_id_str, order_product in order.products.items():
                worksheet.write(cls.row, product_column_dict[campaing_product_id_str], order_product.get('qty', 0))
            cls._next_row()
            cls._reset_column()
        cls._reset_row()

        workbook.close()
        buffer.seek(0)
        return buffer
