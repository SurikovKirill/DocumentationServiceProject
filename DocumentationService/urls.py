from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter(trailing_slash=False)
# router.register(r'tasks', views.TasksViewSet)
router.register(r'root', views.SpecViewSet)

urlpatterns = [
    path(r'apiv1/', include(router.urls)),
    path(r'roots', views.AllRootsView.as_view()),
    path(r'components/<int:pk>', views.ComponentView.as_view()),
    path(r'insert', views.InsertationRoot.as_view()),
    path(r'api/object', views.ObjectAPI.as_view()),
    path(r'apiv1/object/<int:pk>', views.ObjectAPIGet.as_view())
]