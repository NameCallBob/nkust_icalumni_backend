from rest_framework import viewsets, status
from rest_framework.decorators import action , authentication_classes , permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser , AllowAny
from django.shortcuts import get_object_or_404
from apps.Info.models import (
    AlumniAssociation,
    AlumniAssociationImage,
    Constitution,
    ConstitutionImage,
    OrganizationalStructure,
    OrganizationalStructureImage,
    MembershipRequirement,
    MembershipRequirementImage,
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




# 章程 ViewSet
class MembershipRequirementViewSet(viewsets.ViewSet):
    """章程 ViewSet"""

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
