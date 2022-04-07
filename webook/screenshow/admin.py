from django.contrib import admin
from webook.screenshow.models import (DisplayLayout, DisplayLayoutSetting, ScreenGroup, ScreenResource, )


admin.site.register([
    DisplayLayout,
    DisplayLayoutSetting,
    ScreenGroup,
    ScreenResource
])

