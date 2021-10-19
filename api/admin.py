from django.contrib import admin
from .models import (
    sample,
)

admin.site.register(sample.Sample,
                    sample.SampleAdmin)
