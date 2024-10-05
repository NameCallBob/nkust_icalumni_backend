from rest_framework.routers import SimpleRouter
from apps.member import views
from django.urls import path

router = SimpleRouter()
router.register(r'logined', views.MemberViewSet,basename="member_func")
urlpatterns = router.urls

urlpatterns += [
    path("search/", views.MemberListView.as_view(), name="member_search"),
    path("search_user/", views.MemberListViewForAll.as_view(), name="member_search_notLogined function")

]