from api.utils.common.verify import Verify

from backend.pymongo.mongodb import db
import xlsxwriter, os 


def verify_request(api_user, platform_name, platform_id, campaign_id):
    Verify.verify_user(api_user)
    platform = Verify.get_platform(api_user, platform_name, platform_id)
    campaign = Verify.get_campaign(platform, campaign_id)

    return platform, campaign


#TODO filter by culumn , some column not print in excel 
def generate_order_report(campaign_id, column_list):
    # column_list = ['id', 'customer_name', 'platform', 'email', 'phone', 'first_name', 'last_name', 'gender', 'total', 'tax', 'currency', 'shipping_first_name', 'shipping_last_name', 'shipping_phone', 'shipping_postcode', 'shipping_region', 'shipping_location', 'shipping_address', 'shipping_method']

    campaign_title = db.api_campaign.find_one({'id': campaign_id})['title']
    path = '/mnt/c/Users/derek/Downloads/' + campaign_title + '_order_report.xlsx'

    workbook = xlsxwriter.Workbook(path)
    worksheet = workbook.add_worksheet()
    header = workbook.add_format({
        'bold': True,
        'bg_color': '#F7F7F7',
        'color': 'black',
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    int_center = workbook.add_format({
        'align': 'center'
    })

    row, column = 0, 0
    for column_title in column_list:
        worksheet.write(row, column, column_title, header)
        column += 1
    row += 1
    column = 0

    order_id_list = []
    order_ids = db.api_order.find({'campaign_id': campaign_id})
    for order_id in order_ids:
        order_id_list.append(order_id['id'])
    
    # for each order data 1 by 1
    for order_id in order_id_list:
        order_data = db.api_order.find_one({'id': order_id})

        for column_title in column_list:
            if type(order_data[column_title]) == int or type(order_data[column_title]) == float:
                worksheet.write(row, column, order_data[column_title], int_center)
            else:
                worksheet.write(row, column, order_data[column_title])

            if len(str(order_data[column_title])) > 8:
                worksheet.set_column(row, column, len(str(order_data[column_title])))
            else:
                worksheet.set_column(row, column, 8)

            column += 1
        row += 1
        column = 0

        print (order_data['customer_id'])
    
    workbook.close()