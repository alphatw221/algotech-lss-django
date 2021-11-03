import csv
# Import models from models directory
from api.utilities.api_orm_utilities import *


def create_fb_campaign_summary(campaign_id, file_name=None, order_status=None):
    product_descriptions = orm_get_product_descriptions_of_campaign(
        campaign_id)

    folder_dir = './report/'
    if file_name is None:
        file_name = f'campaign_summary_{str(campaign_id)}.csv'
    else:
        file_name = f'{file_name}.csv'

    with open(folder_dir + file_name, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile, quotechar='"', quoting=csv.QUOTE_ALL)

        csh = CampaignSummaryHelper(product_descriptions)

        column_titles = csh.get_column_titles()
        writer.writerow(column_titles)

        orders = orm_get_orders(campaign_id, order_status=order_status)
        for order in orders:
            try:
                order_data = csh.get_order_data(order)
                writer.writerow(order_data)
            except:
                pass

    return file_name


class CampaignSummaryHelper():

    def __init__(self, product_descriptions):
        self.product_descriptions = product_descriptions

    def get_column_titles(self):
        column_titles = [
            'Online Order NO',
            'Order time',
            'Facebook Name',
            'Name',
            'Phone',
            'Email',
            'Address',
            'Postal Code',
            'Delivery Way',
            'In-store Time',
            'Shipping Date',
            'Shipping Time',
            'Delivery/ Collection Date',
            'Delivery Time',
            'Sub Total',
            'Order Status',
            'Remarks',
            'Payment Method',
            'Payment Info',
            'Payment Return',
            'Payment Card Type',
            'Payment Card Number',
            'Internal remarks'
        ]
        for product_description in self.product_descriptions:
            column_titles.append(getattr(product_description, 'name', ''))

        return column_titles

    def get_order_data(self, order):
        def _get_name(order_user_metas_dict):
            if 'shipping_first_name' in order_user_metas_dict or \
                    'shipping_last_name' in order_user_metas_dict:
                return f"{order_user_metas_dict.get('shipping_first_name', '')} {order_user_metas_dict.get('shipping_last_name', '')}"
            else:
                return 'N/A'

        def _get_fb_user_name(order):
            campaign_comment = orm_get_fb_campaign_comment_by_fb_user_id(
                order.fb_user_id)
            return campaign_comment.fb_user_name if campaign_comment else 'N/A'

        def _get_order_related_infos(order):
            order_metas = orm_get_order_metas(order_id=order.id)
            order_user_metas = orm_get_order_user_metas(order_id=order.id)
            order_products = orm_get_order_products(order.id)

            meta_d, user_metas_d, products_d = {}, {}, {}
            for order_meta in order_metas:
                meta_d[order_meta.meta_key] = order_meta.meta_value
            for order_user_meta in order_user_metas:
                user_metas_d[order_user_meta.meta_key] = order_user_meta.meta_value
            for order_product in order_products:
                if order_product.quantity > 0:
                    if order_product.product_id in products_d:
                        products_d[order_product.product_id].quantity += order_product.quantity
                    else:
                        products_d[order_product.product_id] = order_product

            return meta_d, user_metas_d, products_d

        def _get_address(user_metas_d):
            address = 'N/A'
            delivery_way = user_metas_d.get('delivery_way', None)

            if delivery_way == 'in_store_pickup':
                address = user_metas_d.get('store_branch', 'N/A')
            elif delivery_way == 'shipping':
                address = user_metas_d.get('shipping_address', 'N/A')
            return address

        # init data
        meta_d, user_metas_d, products_d = _get_order_related_infos(order)
        order_data = list()

        # writing data
        order_data.append(order.id)
        order_data.append(order.modified_time)
        order_data.append(_get_fb_user_name(order))
        order_data.append(_get_name(user_metas_d))
        order_data.append(user_metas_d.get('shipping_phone', 'N/A'))
        order_data.append(user_metas_d.get('shipping_email', 'N/A'))
        order_data.append(_get_address(user_metas_d))
        order_data.append(user_metas_d.get('shipping_post_code', 'N/A'))
        order_data.append(user_metas_d.get('delivery_way', 'N/A'))
        order_data.append(user_metas_d.get('in_store_time', 'N/A'))
        order_data.append(user_metas_d.get('shipping_date', 'N/A'))
        order_data.append(user_metas_d.get('shipping_time', 'N/A'))
        order_data.append('N/A')
        order_data.append('N/A')
        order_data.append(f'{order.total:.2f}')
        order_data.append(order.order_status)
        order_data.append(user_metas_d.get('shipping_remarks', 'N/A'))
        order_data.append(meta_d.get('payment_method', 'N/A'))
        order_data.append(meta_d.get('payment_info', 'N/A'))
        order_data.append(meta_d.get('general_payment_return', 'N/A'))
        order_data.append(meta_d.get('payment_info_ccbrand', 'N/A'))
        order_data.append(meta_d.get('payment_info_cardnumber', 'N/A'))
        order_data.append('N/A')
        # Show qty of the buying product
        for product_description in self.product_descriptions:
            order_product = products_d.get(
                product_description.product_id, None)
            order_data.append(
                order_product.quantity if order_product else '')

        return order_data
