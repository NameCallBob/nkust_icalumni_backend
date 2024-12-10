from rest_framework.routers import SimpleRouter
from apps.Info.views import (
    MembershipRequirementViewSet,
    AlumniAssociationViewSet,
    ConstitutionViewSet,
    OrganizationalStructureViewSet,
)
from apps.Info.views_pic import (
    AlumniAssociationImageViewSet,
    ConstitutionImageViewSet,
    OrganizationalStructureImageViewSet,
    MembershipRequirementImageViewSet,
)

# 初始化 Router
router = SimpleRouter()

# 註冊 ViewSet
router.register(r'association-images', AlumniAssociationImageViewSet, basename='alumni-association-image')
router.register(r'constitution-images', ConstitutionImageViewSet, basename='constitution-image')
router.register(r'structure-images', OrganizationalStructureImageViewSet, basename='organizational-structure-image')
router.register(r'requirement-images', MembershipRequirementImageViewSet, basename='membership-requirement-image')

router.register(r'associations', AlumniAssociationViewSet, basename='alumni-association')
router.register(r'constitutions', ConstitutionViewSet, basename='constitution')
router.register(r'structures', OrganizationalStructureViewSet, basename='organizational-structure')
router.register(r'requirement', MembershipRequirementViewSet, basename='membership-requirement-image')

urlpatterns = router.urls