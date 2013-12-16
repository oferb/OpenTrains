from django.contrib import admin
import models

# Register your models here.
cls_list = models.GTFSModel.__subclasses__()  # @UndefinedVariable
for cls in cls_list: 
    admin.site.register(cls)
    
    
