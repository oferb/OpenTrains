from django.contrib import admin
import common.ot_utils
import models

class ReportAdmin(admin.ModelAdmin):
    list_filter = ('device_id',)
    
admin.site.register(models.Report,ReportAdmin)
common.ot_utils.autoregister('analysis')

