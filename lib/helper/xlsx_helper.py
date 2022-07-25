from api import models
import xlsxwriter
import io

class FieldMapper():
    field_name=''
    title=''
    def __init__(self, field_name=None, title=None, width=None):
        if field_name!=None:
            self.field_name = field_name
        if title!=None:
            self.title = title
        if width!=None:
            self._width = width
            
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

class CustomerNameMapper(FieldMapper):
    def mapping(self, object):
        return  f'{object.shipping_last_name} {object.shipping_first_name}'

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
        info_data = '' if shipping_method == models.order.order.SHIPPING_METHOD_PICKUP else super().mapping(object)
        return info_data
class PickupInfoMapper(FieldMapper):
    def mapping(self, object):
        shipping_method=getattr(object, 'shipping_method')
        info_data = '' if shipping_method == models.order.order.SHIPPING_METHOD_DELIVERY else super().mapping(object)
        return info_data

class PaymentMethodMapper(FieldMapper):
    def mapping(self, object):
        data = f'{super().mapping(object)} - {object.meta.get("account_mode", "")}' if object.payment_method == 'Direct Payment' else super().mapping(object)
        return data
class LastFiveDigitMapper(FieldMapper):
    def mapping(self, object):
        return object.meta.get(self.field_name, '')

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
            FieldMapper('id','ID'),
            DateTimeMapper('created_at','Order Date'),
            FieldMapper('platform','Platform'),
            CustomerNameMapper('customer_name','Customer Name'),
            FieldMapper('shipping_phone','Shipping Phone'),
            FieldMapper('shipping_email','E-mail'),
            ShippingMethodMapper('shipping_method','Shipping Method'),
            ShippingOptionMapper('shipping_option','Shipping Option'),
            DeliveryInfonMapper('shipping_address_1','Shipping Address 1'),
            DeliveryInfonMapper('shipping_location','Location'),
            DeliveryInfonMapper('shipping_region','Region'),
            DeliveryInfonMapper('shipping_postcode','Postcode'),
            # PickupInfoMapper('pick_up_store','Pick Up Store'),
            PickupInfoMapper('pickup_address','Pick Up Addrwess'),
            FieldMapper('shipping_remark','Remark'),
            PaymentMethodMapper('payment_method','Payment Method'),
            FieldMapper('status','Payment Status'),
            LastFiveDigitMapper('last_five_digit','Payment Record'),
            FieldMapper('total','Total'),
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
        worksheet.merge_range(cls.row, 0, cls.row, len(cls.columns) + campaign_products_count - 1, campaign.title + ' Order Report', title_format)
        cls._next_row()
        worksheet.merge_range(cls.row, 0, cls.row, 5, 'Contact Info', info_format)
        worksheet.merge_range(cls.row, 6, cls.row, 14, 'Delivery Info', info_format)
        worksheet.merge_range(cls.row, 15, cls.row, 18, 'Payment Info', info_format)
        worksheet.merge_range(cls.row, 19, cls.row, 19 + campaign_products_count - 1, 'Order Info', info_format)
        cls._next_row()

        for column in cls.columns:
            worksheet.write(cls.row, cls.col, column.title, header_format)
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
                worksheet.write(cls.row, cls.col, column.mapping(order))
                cls._next_column()

            for campaing_product_id_str, order_product in order.products.items():
                worksheet.write(cls.row, product_column_dict[campaing_product_id_str], order_product.get('qty', 0))
            cls._next_row()
            cls._reset_column()

        workbook.close()
        buffer.seek(0)
        return buffer