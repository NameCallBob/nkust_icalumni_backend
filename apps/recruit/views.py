from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from apps.recruit.models import Recruit
from apps.recruit.serializer import RecruitSerializer

# 分頁器
class RecruitPagination(PageNumberPagination):
    page_size = 10  # 每頁顯示 10 筆資料
    page_size_query_param = 'page_size'
    max_page_size = 100

class RecruitViewSet(viewsets.ViewSet):
    """
    處理 Recruit 的 CRUD 操作，查詢功能支持分頁
    """

    # 查詢所有招聘資料，並進行分頁
    def list(self, request):
        queryset = Recruit.objects.all()
        paginator = RecruitPagination()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = RecruitSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = RecruitSerializer(queryset, many=True)
        return Response(serializer.data)

    # 查詢單一招聘資料
    def retrieve(self, request):
        try:
            pk = request.data.get("id",'')
            if pk == "":
                return Response({"msg":"Id ?"} , status=status.HTTP_400_BAD_REQUEST)
            recruit = Recruit.objects.get(pk=pk)
        except Recruit.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = RecruitSerializer(recruit)
        return Response(serializer.data)

    # 創建招聘資料
    def create(self, request):
        serializer = RecruitSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 更新招聘資料
    def update(self, request):
        try:
            pk = request.data.get("pk")
            if pk == "":
                return Response({"msg":"Id ?"} , status=status.HTTP_400_BAD_REQUEST)
            recruit = Recruit.objects.get(pk=pk)

        except Recruit.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = RecruitSerializer(recruit, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 刪除招聘資料
    def destroy(self, request):
        try:
            pk = request.data.get("pk")
            if pk == "":
                return Response({"msg":"Id ?"} , status=status.HTTP_400_BAD_REQUEST)
            recruit = Recruit.objects.get(pk=pk)
        except Recruit.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        recruit.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
