from .default import DefaultDiscountCodeImportProcessor, CONTENT_TYPE_CSV, CONTENT_TYPE_XLSX

from api import models


class SHCDiscountCodeImportProcessor(DefaultDiscountCodeImportProcessor):

    def __init__(self, user_subscription, size_limit_bytes=100 * 1024 * 1024, accept_types=[CONTENT_TYPE_XLSX, CONTENT_TYPE_CSV]) -> None:
        self.sheet_name = 'bal'
        super().__init__(user_subscription, size_limit_bytes, accept_types)

    

    def save_data(self, data):
        cache_object = {}
        users = []
        for i, (first_object, second_object) in enumerate(zip(data[:-1],data[1:])):
            try:
                if not second_object.get('Promo Code') and not second_object.get('Amount'):
                    if not cache_object:
                        cache_object = first_object
                    users.append(first_object.get('Name'))   
                    
                    continue

                if users:
                    users.append(first_object.get('Name'))
                    data = self.__get_merge_data(cache_object, users)
                    models.discount_code.discount_code.DiscountCode.objects.create(**data)
                    cache_object = {}
                    users = []
                    continue
                
                data = self.__get_model_data(first_object)
                models.discount_code.discount_code.DiscountCode.objects.create(**data)

                if i == len(data)-2:
                    data = self.__get_model_data(second_object)
                    models.discount_code.discount_code.DiscountCode.objects.create(**data)
                
                

                
            except Exception:
                import traceback
                print(traceback.format_exc())

    def __get_model_data(self, object, names = []):
        return {
                    'name':object.get('Promo Code'),
                    'user_subscription':self.user_subscription,
                    'type':models.discount_code.discount_code.TYPE_GENERAL,
                    'discount_type':models.discount_code.discount_code.DISCOUNT_TYPE_DEDUCT,
                    'period_enabled':False,
                    'code':object.get('Promo Code'),
                    'description':object.get('Reason'),                    
                    'limitations':[ {
                        "key": models.discount_code.discount_code.LIMITATION_SPECIFIC_BUYER_NAME,
                        "names": object.get('Name') if not names else ','.join(names)
                    },
                    {
                        "key": models.discount_code.discount_code.LIMITATION_BUYER_USAGE_TIMES,
                        "times": 1
                    }
                    ],
                    'meta':{
                         "deduct_amount":object.get('Amount')
                    }
                }

    def __get_merge_data(self, object, users):
        return self.__get_model_data(object, users)