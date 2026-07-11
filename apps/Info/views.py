from rest_framework import viewsets, status
from rest_framework.decorators import action , authentication_classes , permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser , AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from apps.Info.models import (
    AlumniAssociation,
    AlumniAssociationImage,
    Constitution,
    ConstitutionImage,
    OrganizationalStructure,
    OrganizationalStructureImage,
    MembershipRequirement,
    MembershipRequirementImage,
    MembershipRequirement_v2,
)
from apps.Info.serializer import (
    AlumniAssociationSerializer,
    AlumniAssociationImageSerializer,
    ConstitutionSerializer,
    ConstitutionImageSerializer,
    OrganizationalStructureSerializer,
    OrganizationalStructureImageSerializer,
    MembershipRequirementSerializer,
    MembershipRequirementImageSerializer,
    MembershipRequirementSerializer_v2,
)


# 系友會 ViewSet
class AlumniAssociationViewSet(viewsets.ViewSet):
    """系友會 ViewSet"""
    @action(detail=False, methods=["get"], permission_classes=[AllowAny] , authentication_classes=[])
    def latest(self, request):
        """查詢最近更新的系友會資料"""
        instance = AlumniAssociation.objects.order_by("-updated_at").first()
        if instance:
            serializer = AlumniAssociationSerializer(instance)
            return Response(serializer.data)
        return Response({"detail": "無資料"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["get"], permission_classes=[IsAdminUser] , authentication_classes=[JWTAuthentication])
    def all(self, request):
        """查詢最近更新的系友會資料"""
        instance = AlumniAssociation.objects.order_by("-updated_at").all()
        if instance:
            serializer = AlumniAssociationSerializer(instance,many=True)
            return Response(serializer.data)
        return Response({"detail": "無資料"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["post"], permission_classes=[IsAdminUser], authentication_classes=[JWTAuthentication])
    def new(self, request):
        """新增系友會資料（限管理員）"""
        serializer = AlumniAssociationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["put"], permission_classes=[IsAdminUser], authentication_classes=[JWTAuthentication])
    def change(self, request):
        """更新系友會資料（限管理員）"""
        association_id = request.data.get("id")
        if not association_id:
            return Response({"detail": "缺少 id"}, status=status.HTTP_400_BAD_REQUEST)
        instance = get_object_or_404(AlumniAssociation, id=association_id)
        serializer = AlumniAssociationSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["delete"], permission_classes=[IsAdminUser], authentication_classes=[JWTAuthentication])
    def remove(self, request):
        """刪除系友會資料（限管理員）"""
        association_id = request.data.get("id")
        if not association_id:
            return Response({"detail": "缺少 id"}, status=status.HTTP_400_BAD_REQUEST)
        instance = get_object_or_404(AlumniAssociation, id=association_id)
        instance.delete()
        return Response({"detail": "系友會已刪除"}, status=status.HTTP_204_NO_CONTENT)



from rest_framework.parsers import MultiPartParser, FormParser , JSONParser

# 章程 ViewSet
class ConstitutionViewSet(viewsets.ViewSet):
    """章程 ViewSet"""
    parser_classes = [MultiPartParser, FormParser , JSONParser]

    @action(detail=False, methods=["get"], permission_classes=[AllowAny] , authentication_classes=[])
    def latest(self, request):
        """查詢最近更新的系友會資料"""
        instance = Constitution.objects.order_by("-updated_at").first()
        if instance:
            serializer = ConstitutionSerializer(instance)
            return Response(serializer.data)
        return Response({"detail": "無資料"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["get"], permission_classes=[IsAdminUser] , authentication_classes=[JWTAuthentication])
    def all(self, request):
        """查詢最近更新的系友會資料"""
        instance = Constitution.objects.all().order_by("-updated_at")
        if instance:
            serializer = ConstitutionSerializer(instance,many=True)
            return Response(serializer.data)
        return Response({"detail": "無資料"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["post"], permission_classes=[IsAdminUser], authentication_classes=[JWTAuthentication])
    def new(self, request):
        """新增章程（限管理員）"""
        serializer = ConstitutionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["put"], permission_classes=[IsAdminUser], authentication_classes=[JWTAuthentication])
    def change(self, request):
        """更新章程資料（限管理員）"""
        constitution_id = request.data.get("id")
        if not constitution_id:
            return Response({"detail": "缺少 id"}, status=status.HTTP_400_BAD_REQUEST)
        instance = get_object_or_404(Constitution, id=constitution_id)
        serializer = ConstitutionSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["delete"], permission_classes=[IsAdminUser], authentication_classes=[JWTAuthentication])
    def remove(self, request):
        """刪除章程資料（限管理員）"""
        id = request.data.get("id")
        if not id:
            return Response({"detail": "缺少 id"}, status=status.HTTP_400_BAD_REQUEST)
        instance = get_object_or_404(Constitution, id=id)
        instance.delete()
        return Response({"detail": "章程已刪除"}, status=status.HTTP_204_NO_CONTENT)

# 組織 ViewSet
class OrganizationalStructureViewSet(viewsets.ViewSet):
    """系友會 ViewSet"""

    @action(detail=False, methods=["get"], permission_classes=[AllowAny] , authentication_classes=[])
    def latest(self, request):
        """查詢最近更新的系友會資料"""
        instance = OrganizationalStructure.objects.order_by("-updated_at").first()
        if instance:
            serializer = OrganizationalStructureSerializer(instance)
            return Response(serializer.data)
        return Response({"detail": "無資料"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["get"], permission_classes=[IsAdminUser] , authentication_classes=[JWTAuthentication])
    def all(self, request):
        """查詢最近更新的系友會資料"""
        instance = OrganizationalStructure.objects.order_by("-updated_at").all()
        if instance:
            serializer = OrganizationalStructureSerializer(instance,many=True)
            return Response(serializer.data)
        return Response({"detail": "無資料"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["post"], permission_classes=[IsAdminUser], authentication_classes=[JWTAuthentication])
    def new(self, request):
        """新增系友會資料（限管理員）"""
        serializer = OrganizationalStructureSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["put"], permission_classes=[IsAdminUser], authentication_classes=[JWTAuthentication])
    def change(self, request):
        """更新系友會資料（限管理員）"""
        id = request.data.get("id")
        if not id:
            return Response({"detail": "缺少 id"}, status=status.HTTP_400_BAD_REQUEST)
        instance = get_object_or_404(OrganizationalStructure, id=id)
        serializer = OrganizationalStructureSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["delete"], permission_classes=[IsAdminUser], authentication_classes=[JWTAuthentication])
    def remove(self, request):
        """刪除系友會資料（限管理員）"""
        id = request.data.get("id")
        if not id:
            return Response({"detail": "缺少 id"}, status=status.HTTP_400_BAD_REQUEST)
        instance = get_object_or_404(OrganizationalStructure, id=id)
        instance.delete()
        return Response({"detail": "系友會已刪除"}, status=status.HTTP_204_NO_CONTENT)




# 入會條件 ViewSet
class MembershipRequirementViewSet(viewsets.ViewSet):
    """入會條件 ViewSet"""

    @action(detail=False, methods=["get"], permission_classes=[AllowAny] , authentication_classes=[])
    def latest(self, request):
        """查詢最近更新的系友會資料"""
        instance = MembershipRequirement.objects.order_by("-updated_at").first()
        if instance:
            serializer = MembershipRequirementSerializer(instance)
            return Response(serializer.data)
        return Response({"detail": "無資料"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["get"], permission_classes=[IsAdminUser] , authentication_classes=[JWTAuthentication])
    def all(self, request):
        """查詢最近更新的系友會資料"""
        instance = MembershipRequirement.objects.all().order_by("-updated_at")
        if instance:
            serializer = MembershipRequirementSerializer(instance,many=True)
            return Response(serializer.data)
        return Response({"detail": "無資料"}, status=status.HTTP_404_NOT_FOUND)


    @action(detail=False, methods=["post"], permission_classes=[IsAdminUser], authentication_classes=[JWTAuthentication])
    def new(self, request):
        """新增章程（限管理員）"""
        serializer = MembershipRequirementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["put"], permission_classes=[IsAdminUser], authentication_classes=[JWTAuthentication])
    def change(self, request):
        """更新章程資料（限管理員）"""
        id = request.data.get("id")
        if not id:
            return Response({"detail": "缺少 id"}, status=status.HTTP_400_BAD_REQUEST)
        instance = get_object_or_404(MembershipRequirement, id=id)
        serializer = MembershipRequirementSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["delete"], permission_classes=[IsAdminUser], authentication_classes=[JWTAuthentication])
    def remove(self, request):
        """刪除章程資料（限管理員）"""
        id = request.data.get("id")
        if not id:
            return Response({"detail": "缺少 id"}, status=status.HTTP_400_BAD_REQUEST)
        instance = get_object_or_404(MembershipRequirement, id=id)
        instance.delete()
        return Response({"detail": "章程已刪除"}, status=status.HTTP_204_NO_CONTENT)


class MembershipRequirementViewSet_v2(viewsets.ViewSet):
    """入會條件 ViewSet"""
    parser_classes = [MultiPartParser, FormParser , JSONParser]
    
    @action(detail=False, methods=["get"], permission_classes=[AllowAny], authentication_classes=[])
    def latest(self, request):
        """查詢最近更新的入會條件資料"""
        instance = MembershipRequirement_v2.objects.order_by("-updated_at").first()
        if instance:
            serializer = MembershipRequirementSerializer_v2(instance, context={'request': request})
            return Response(serializer.data)
        return Response({"detail": "無資料"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["get"], permission_classes=[IsAdminUser], authentication_classes=[JWTAuthentication])
    def all(self, request):
        """查詢所有入會條件資料（限管理員）"""
        instance = MembershipRequirement_v2.objects.all().order_by("-updated_at")
        if instance:
            serializer = MembershipRequirementSerializer_v2(instance, many=True, context={'request': request})
            return Response(serializer.data)
        return Response({"detail": "無資料"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["post"], permission_classes=[IsAdminUser], authentication_classes=[JWTAuthentication])
    def new(self, request):
        """新增入會條件（限管理員）"""
        serializer = MembershipRequirementSerializer_v2(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["put"], permission_classes=[IsAdminUser], authentication_classes=[JWTAuthentication])
    def change(self, request):
        """更新入會條件資料（限管理員）"""
        id = request.data.get("id")
        if not id:
            return Response({"detail": "缺少 id"}, status=status.HTTP_400_BAD_REQUEST)
        instance = get_object_or_404(MembershipRequirement_v2, id=id)
        serializer = MembershipRequirementSerializer_v2(instance, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["delete"], permission_classes=[IsAdminUser], authentication_classes=[JWTAuthentication])
    def remove(self, request):
        """刪除入會條件資料（限管理員）"""
        id = request.data.get("id")
        if not id:
            return Response({"detail": "缺少 id"}, status=status.HTTP_400_BAD_REQUEST)
        instance = get_object_or_404(MembershipRequirement_v2, id=id)
        instance.delete()
        return Response({"detail": "入會條件已刪除"}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], permission_classes=[AllowAny], authentication_classes=[])
    def download_pdf(self, request):
        """下載最新的入會條件 PDF 檔案"""
        id = request.query_params.get("id")
        if not id:
            return Response({"detail": "缺少 id 參數"}, status=status.HTTP_400_BAD_REQUEST)

        instance = get_object_or_404(MembershipRequirement_v2, id=id)

        if not instance.pdf_file:
            return Response({"detail": "此入會條件沒有 PDF 檔案"}, status=status.HTTP_404_NOT_FOUND)

        try:
            response = HttpResponse(
                instance.pdf_file.read(),
                content_type='application/pdf'
            )
            response['Content-Disposition'] = f'attachment; filename="membership_requirement_{id}.pdf"'
            return response
        except Exception as e:
            # [資安修補 SEC-024/SEC-022] 不向用戶端外洩例外細節，僅回通用訊息（細節由 log 記錄）。
            return Response({"detail": "下載失敗，請稍後再試"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # [修正] 方法名稱不可為 detail：會與 DRF ViewSet 的 self.detail(bool) 屬性衝突，
    # 導致路由解析到布林值而非方法（TypeError: 'bool' object is not callable）。
    # 改名為 detail_view，並以 url_path 保持對外路徑仍為 /detail/。
    @action(detail=False, methods=["get"], url_path="detail", permission_classes=[AllowAny], authentication_classes=[])
    def detail_view(self, request):
        """查詢特定入會條件詳細資料"""
        id = request.query_params.get("id")
        if not id:
            return Response({"detail": "缺少 id 參數"}, status=status.HTTP_400_BAD_REQUEST)

        instance = get_object_or_404(MembershipRequirement_v2, id=id)
        serializer = MembershipRequirementSerializer_v2(instance, context={'request': request})
        return Response(serializer.data)