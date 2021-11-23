from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer, TokenVerifySerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        auth_user_id = token['user_id']
        del token['user_id']
        if user.api_users.filter(type='user').exists():
            seller = user.api_users.get(type='user')
            name = seller.name

        if user.api_users.filter(type='customer').exists():
            customer = user.api_users.get(type='customer')
            name = seller.name

        token['data'] = {
            'auth_user_id': auth_user_id,
            'seller_id': seller.id if seller else None,
            'customer_id': customer.id if customer else None,
            'name': name,
        }

        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        auth_user_id = token['user_id']
        del token['user_id']
        if user.api_users.filter(type='user').exists():
            seller = user.api_users.get(type='user')
            name = seller.name

        if user.api_users.filter(type='customer').exists():
            customer = user.api_users.get(type='customer')
            name = seller.name

        token['data'] = {
            'auth_user_id': auth_user_id,
            'seller_id': seller.id if seller else None,
            'customer_id': customer.id if customer else None,
            'name': name,
        }

        return token


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenVerifySerializer(TokenVerifySerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        auth_user_id = token['user_id']
        del token['user_id']
        if user.api_users.filter(type='user').exists():
            seller = user.api_users.get(type='user')
            name = seller.name

        if user.api_users.filter(type='customer').exists():
            customer = user.api_users.get(type='customer')
            name = seller.name

        token['data'] = {
            'auth_user_id': auth_user_id,
            'seller_id': seller.id if seller else None,
            'customer_id': customer.id if customer else None,
            'name': name,
        }

        return token


class CustomTokenVerifyView(TokenVerifyView):
    serializer_class = CustomTokenVerifySerializer
