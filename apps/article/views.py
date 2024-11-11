from rest_framework import viewsets, status , permissions
from rest_framework.decorators import action , authentication_classes , permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from apps.article.models import Article
from apps.article.serializer import ArticleSerializer,ArticleSerializer_TableOutput

# drf_yasg
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class ArticleViewSet(viewsets.ViewSet):
    """
    處理文章的 CRUD 操作，同時處理文章圖片
    """

    @swagger_auto_schema(
        operation_description="查詢所有文章_已發布",
        responses={200: '成功返回所有文章'}
    )
    @action(methods=['get'], detail=False, authentication_classes=[], permission_classes=[permissions.AllowAny])
    def all_active(self, request):
        queryset = Article.objects.filter(active=True).order_by('-created_at')
        serializer = ArticleSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="查詢所有文章_已發布",
        responses={200: '成功返回所有文章'}
    )
    @action(methods=['get'], detail=False, authentication_classes=[], permission_classes=[permissions.AllowAny])
    def tableOutput(self, request):
        queryset = Article.objects.filter(active=True).order_by('-created_at')
        serializer = ArticleSerializer_TableOutput(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="查詢所有文章",
        responses={200: '成功返回所有文章'}
    )
    @action(methods=['get'], detail=False, authentication_classes=[], permission_classes=[permissions.AllowAny])
    def all(self, request):
        queryset = Article.objects.all().order_by('-created_at')
        serializer = ArticleSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="查詢單一文章",
        responses={
            200: '成功返回文章',
            404: '文章不存在',
            400: '資料鍵錯誤'
        },
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description="文章ID", type=openapi.TYPE_INTEGER)
        ]
    )
    @action(methods=['get'], detail=False, authentication_classes=[], permission_classes=[permissions.AllowAny])
    def get_one(self, request):
        try:
            pk = request.GET['id']
            article = Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        except KeyError:
            return Response({'msg': "datakey not correct!"}, status=status.HTTP_400_BAD_REQUEST)

        article.view_count += 1
        article.save()

        serializer = ArticleSerializer(article)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="創建新文章並上傳圖片",
        request_body=ArticleSerializer,
        responses={
            201: '創建成功',
            400: '資料無效'
        }
    )
    @action(methods=['post'], detail=False, authentication_classes=[JWTAuthentication], permission_classes=[permissions.IsAuthenticated])
    def new(self, request):
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="更新文章和圖片",
        request_body=ArticleSerializer,
        responses={
            200: '更新成功',
            404: '文章不存在',
            400: '資料無效'
        }
    )
    @action(methods=['patch'], detail=False, authentication_classes=[JWTAuthentication], permission_classes=[permissions.IsAuthenticated])
    def change(self, request):
        try:
            pk = request.data.get("id", '')
            if pk == "":
                return Response({"msg": "id not given"}, status=status.HTTP_400_BAD_REQUEST)
            article = Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ArticleSerializer(article, data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="刪除文章",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description="文章ID")
            },
            required=['id']
        ),
        responses={
            204: '刪除成功',
            404: '文章不存在',
            400: '資料無效'
        }
    )
    @action(methods=['delete'], detail=False, authentication_classes=[JWTAuthentication], permission_classes=[permissions.IsAuthenticated])
    def delete(self, request):
        try:
            pk = request.data.get("id", '')
            if pk == "":
                return Response({"msg": "id not given"}, status=status.HTTP_400_BAD_REQUEST)
            article = Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)