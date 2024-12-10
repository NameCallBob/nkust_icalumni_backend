from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action , authentication_classes , permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from apps.recruit.models import Recruit
from apps.recruit.serializer import RecruitSerializer,RecruitSerializer_forTable,RecruitAdminSerializer_forTable
from rest_framework_simplejwt.authentication import JWTAuthentication
# drf_yasg
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class RecruitPagination(PageNumberPagination):
    page_size = 10  # 每頁顯示 10 筆資料
    page_size_query_param = 'page_size'
    max_page_size = 100

class RecruitViewSet(viewsets.ViewSet):
    """
    處理 Recruit 的 CRUD 操作，查詢功能支持分頁
    """
    permission_classes=[permissions.IsAuthenticatedOrReadOnly]
    authentication_classes=[]
    @swagger_auto_schema(
        operation_description="查詢所有招聘資料，並進行分頁",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="頁數", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="每頁顯示資料數", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: openapi.Response('成功', RecruitSerializer(many=True)),
            400: '請求無效'
        }
    )
    @action(methods=['get'] , detail=False , authentication_classes=[] , permission_classes=[])
    def all_active(self, request):
        """查詢所有招聘資料，並進行分頁"""
        queryset = Recruit.objects.all().filter(active=True)
        paginator = RecruitPagination()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = RecruitSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = RecruitSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['get'] , detail=False , authentication_classes=[JWTAuthentication] , permission_classes=[permissions.IsAuthenticated])
    def all(self, request):
        """查詢所有招聘資料，並進行分頁"""
        queryset = Recruit.objects.all()
        paginator = RecruitPagination()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = RecruitSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = RecruitSerializer(queryset, many=True)
        return Response(serializer.data)


    @action(methods=['get'] , detail=False , authentication_classes=[] , permission_classes=[])
    def tableOutput(self,request):
        queryset = Recruit.objects.all().filter(active=True)
        paginator = RecruitPagination()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = RecruitSerializer_forTable(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = RecruitSerializer_forTable(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['get'] , detail=False , authentication_classes=[JWTAuthentication] , permission_classes=[permissions.IsAuthenticated])
    def tableOutput_admin(self, request):
        from apps.member.models import Member
        from apps.company.models import Company
        from rest_framework.generics import get_object_or_404
        from rest_framework.exceptions import NotFound
        # 確認使用者的會員對象是否存在，否則回傳404
        member = get_object_or_404(Member, private=request.user)

        # 確認使用者所屬的公司是否存在，否則回傳404
        company = Company.objects.filter(member=member).first()
        if not company:
            raise NotFound("Company not found for the user.")

        # 查詢啟用的招聘信息
        queryset = Recruit.objects.filter(active=True, company=company)

        # 分頁處理
        paginator = RecruitPagination()
        page = paginator.paginate_queryset(queryset, request)

        # 序列化數據
        if page is not None:
            serializer = RecruitAdminSerializer_forTable(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = RecruitAdminSerializer_forTable(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="查詢單一招聘資料",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description="招聘 ID", type=openapi.TYPE_STRING),
        ],
        responses={
            200: RecruitSerializer,
            404: '招聘資料不存在',
            400: '請求無效'
        }
    )
    @action(methods=['get'] , detail=False , authentication_classes=[] , permission_classes=[])
    def getOne(self, request):
        """查詢單一招聘資料"""
        try:
            pk = request.query_params.get("id", '')
            if pk == "":
                return Response({"msg": "Id ?"}, status=status.HTTP_400_BAD_REQUEST)
            recruit = Recruit.objects.get(pk=pk)
        except Recruit.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = RecruitSerializer(recruit)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="創建招聘資料",
        request_body=RecruitSerializer,
        responses={
            201: openapi.Response('創建成功', RecruitSerializer),
            400: '請求無效'
        }
    )
    @action(methods=['post'], detail=False, authentication_classes=[JWTAuthentication], permission_classes=[permissions.IsAuthenticated])
    def new(self, request):
        """創建招聘資料"""
        from apps.company.models import Company
        tmp = request.data.copy()  # 確保 data 可變動
        tmp['company'] = Company.objects.get(member=request.user.member).id
        serializer = RecruitSerializer(data=tmp, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="更新招聘資料",
        request_body=RecruitSerializer,
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description="招聘 ID", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response('更新成功', RecruitSerializer),
            404: '招聘資料不存在',
            400: '請求無效'
        }
    )
    @action(methods=['put'] , detail=False , authentication_classes=[JWTAuthentication] , permission_classes=[permissions.IsAuthenticated])
    def change(self, request):
        """更新招聘資料"""
        try:
            pk = request.data.get("id")
            if pk == "":
                return Response({"msg": "Id ?"}, status=status.HTTP_400_BAD_REQUEST)
            recruit = Recruit.objects.get(pk=pk)
        except Recruit.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = RecruitSerializer(recruit, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="刪除招聘資料",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description="招聘 ID", type=openapi.TYPE_STRING),
        ],
        responses={
            204: '成功刪除',
            404: '招聘資料不存在',
            400: '請求無效'
        }
    )
    @action(methods=['delete'] , detail=False , authentication_classes=[JWTAuthentication] , permission_classes=[permissions.IsAuthenticated])
    def delete(self, request):
        """刪除招聘資料"""
        try:
            pk = request.GET["id"]
            if pk == "":
                return Response({"msg": "Id ?"}, status=status.HTTP_400_BAD_REQUEST)
            recruit = Recruit.objects.get(pk=pk)
        except KeyError:
            return Response("id?",status=400)
        except Recruit.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        recruit.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
