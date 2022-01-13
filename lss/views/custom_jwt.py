from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer, TokenVerifySerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user, platform_name='facebook'):
        token = super().get_token(user)
        auth_user_id = token['user_id']
        seller = None
        customer = None
        seller_image = ""
        customer_image = ""

        if user.api_users.filter(type='user').exists():
            seller = user.api_users.get(type='user')
            name = seller.name
            if platform_name == 'facebook':
                seller_image = seller.facebook_info.get('picture','')
            elif platform_name == 'youtube':
                pass
            elif platform_name == 'instagram':
                pass
            

        if user.api_users.filter(type='customer').exists():
            customer = user.api_users.get(type='customer')
            name = customer.name
            if platform_name == 'facebook':
                customer_image = customer.facebook_info.get('picture','')
            elif platform_name == 'youtube':
                pass
            elif platform_name == 'instagram':
                pass


        token['data'] = {
            'auth_user_id': auth_user_id,
            'seller_id': seller.id if seller else "",
            'customer_id': customer.id if customer else "",
            'name': name,
            'seller_image': seller_image,
            'customer_image': customer_image
        }
        print(token['data'])
        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    @classmethod
    def get_token(cls, user, platform_name='facebook'):
        token = super().get_token(user)
        auth_user_id = token['user_id']
        seller = None
        customer = None
        seller_image = ""
        customer_image = ""

        if user.api_users.filter(type='user').exists():
            seller = user.api_users.get(type='user')
            name = seller.name
            if platform_name == 'facebook':
                seller_image = seller.facebook_info.get('picture','')
            elif platform_name == 'youtube':
                pass
            elif platform_name == 'instagram':
                pass
            

        if user.api_users.filter(type='customer').exists():
            customer = user.api_users.get(type='customer')
            name = customer.name
            if platform_name == 'facebook':
                customer_image = customer.facebook_info.get('picture','')
            elif platform_name == 'youtube':
                pass
            elif platform_name == 'instagram':
                pass


        token['data'] = {
            'auth_user_id': auth_user_id,
            'seller_id': seller.id if seller else "",
            'customer_id': customer.id if customer else "",
            'name': name,
            'seller_image': seller_image,
            'customer_image': customer_image
        }

        return token


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenVerifySerializer(TokenVerifySerializer):
    @classmethod
    def get_token(cls, user, platform_name='facebook'):
        token = super().get_token(user)
        auth_user_id = token['user_id']
        seller = None
        customer = None
        seller_image = ""
        customer_image = ""

        if user.api_users.filter(type='user').exists():
            seller = user.api_users.get(type='user')
            name = seller.name
            if platform_name == 'facebook':
                seller_image = seller.facebook_info.get('picture','')
            elif platform_name == 'youtube':
                pass
            elif platform_name == 'instagram':
                pass
            

        if user.api_users.filter(type='customer').exists():
            customer = user.api_users.get(type='customer')
            name = customer.name
            if platform_name == 'facebook':
                customer_image = customer.facebook_info.get('picture','')
            elif platform_name == 'youtube':
                pass
            elif platform_name == 'instagram':
                pass


        token['data'] = {
            'auth_user_id': auth_user_id,
            'seller_id': seller.id if seller else "",
            'customer_id': customer.id if customer else "",
            'name': name,
            'seller_image': seller_image,
            'customer_image': customer_image
        }

        return token


class CustomTokenVerifyView(TokenVerifyView):
    serializer_class = CustomTokenVerifySerializer
