from django.contrib import admin
from .models import *
import admin_thumbnails

class ProductVariantInlines(admin.TabularInline):
    model = Variants
    extra = 2

@admin_thumbnails.thumbnail('image')
class ImageInlines(admin.TabularInline):
    model = Images
    extra = 2

class CategoryAdmin(admin.ModelAdmin):
    list_display =('name','create','update','sub_category','id')
    list_filter = ('create',)
    prepopulated_fields = {
        'slug':('name',)
    }
    list_editable = ('sub_category',)


class ProductAdmin(admin.ModelAdmin):
    list_display =('name','create','update','amount','available','unit_price','discount','brand','total_favourite','sell','id')
    list_filter = ('available',)
    list_editable = ('amount','unit_price','discount','brand','total_favourite','sell')
    # raw_id_fields = ('category',)
    inlines = [ProductVariantInlines,ImageInlines]

class VariantAdmin(admin.ModelAdmin):
    list_display =('name','id')

class SizeAdmin(admin.ModelAdmin):
    list_display =('name','id')

class BrandAdmin(admin.ModelAdmin):
    list_display =('name','id')

class CommentAdmin(admin.ModelAdmin):
    list_display =('user','create','rate')


admin.site.register(Category,CategoryAdmin)
admin.site.register(Product,ProductAdmin)
admin.site.register(Variants,VariantAdmin)
admin.site.register(Size,SizeAdmin)
admin.site.register(Color)
admin.site.register(Comment,CommentAdmin)
admin.site.register(Images)
admin.site.register(Brand)
admin.site.register(Gallery)
