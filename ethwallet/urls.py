__author__ = 'andrew.shvv@gmail.com'

from django.conf.urls import url, include
from rest_framework_nested import routers

from ethwallet.views import AddressViewSet

router = routers.SimpleRouter()
router.register(prefix=r"addresses", viewset=AddressViewSet, base_name='Address')

urlpatterns = [
    url(r'^v1/', include(router.urls)),
]
