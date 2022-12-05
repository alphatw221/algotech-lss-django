from django.conf import settings
import hubspot


client = hubspot.Client.create(api_key=settings.HUBSPOT_API_KEY)

