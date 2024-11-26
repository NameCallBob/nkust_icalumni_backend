from rest_framework.routers import SimpleRouter
from apps.member import views , other_views , deal_files
from django.urls import path

router = SimpleRouter()
router.register(r'graduate', other_views.GraduateViewSet,basename="member_graduate")
router.register(r'position', other_views.PositionViewSet,basename="member_position")
router.register(r'any', views.MemberAnyViewSet,basename="member_anymous_func")
router.register(r'logined', views.MemberViewSet,basename="member_func")
router.register(r'admin' ,views.MemberAdminViewSet,basename="member_admin_func")
urlpatterns = router.urls

urlpatterns += [
    path("search/", views.MemberListView.as_view(), name="member_search"),
    path("search_user/", views.MemberListViewForAll.as_view(), name="member_search_notLogined function"),
    path("user_add_byExcel", deal_files.UploadExcelView.as_view(), name="member_simple_add_by_Excel")
]