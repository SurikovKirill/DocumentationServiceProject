from django.urls import path, include
from rest_framework import routers

from . import views
#
# router = routers.DefaultRouter(trailing_slash=False)
# router.register(r'tasks', views.TasksViewSet)
# router.register(r'root', views.NodeViewSet)

urlpatterns = [
    path(r'api/object/', views.ObjectAPI.as_view()),
    path(r'api/object/<int:pk>', views.ObjectAPIUpdate.as_view()),
    path(r'api/object/<int:pk>/children', views.ObjectAPIGetChild.as_view()),
    path(r'api/object/<int:pk>/descendants', views.ObjectAPIGetDescendants.as_view()),
    path(r'api/component/', views.ComponentAPI.as_view()),
    path(r'api/component/<int:pk>', views.ComponentAPIGetInfo.as_view()),
    path(r'component/<int:pk>/child', views.ComponentAPIGetChildren.as_view()),
    # path(r'apiv1/', include(router.urls)),
]