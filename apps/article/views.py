import json

from rest_framework import viewsets, status , permissions
from rest_framework.decorators import action , authentication_classes , permission_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from apps.private.cookie_auth import CookieJWTAuthentication as JWTAuthentication  # [資安修補 SEC-015] alias 成 cookie-aware 版本，向下相容 header 認證
from rest_framework.response import Response
from django.db.models import F
from apps.article.models import Article
from apps.article.serializer import ArticleSerializer,ArticleSerializer_TableOutput
from IC_alumni.permission.staff import IsStaffPermission  # [資安修補 HIGH-3]

# drf_yasg
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


def _build_article_request_data(request):
    """
    JSON 請求：images 欄位本身就是巢狀陣列，直接沿用 request.data。

    multipart/form-data 請求：陣列/巢狀物件無法原生表達，前端改用：
      - images_meta：JSON 字串，例如
        '[{"id": 3, "pic_type": "small"}, {"is_new": true, "pic_type": "large"}]'
        （保留既有圖片只帶 id/pic_type；新圖片標記 is_new）
      - image_<index>：對應 images_meta 陣列中該 index 的檔案（僅 is_new 項目需要）

    這裡在丟給 serializer 前，把兩者重組回一般的 images 陣列，並且回傳「一般 dict」
    （而非 QueryDict），因為 DRF 的 ListSerializer 對 QueryDict 輸入會改用
    bracket-notation（images[0]xxx）解析，不會讀取我們直接塞入的巢狀陣列。
    """
    if 'images_meta' not in request.data:
        return request.data

    data = dict(request.data.items())
    data.pop('images_meta', None)

    try:
        images_meta = json.loads(request.data.get('images_meta') or '[]')
    except (ValueError, TypeError):
        images_meta = []

    images_data = []
    for index, item in enumerate(images_meta):
        entry = {'pic_type': item.get('pic_type')}
        if item.get('id'):
            entry['id'] = item['id']
        file_field = f'image_{index}'
        if file_field in request.FILES:
            entry['image'] = request.FILES[file_field]
        images_data.append(entry)

    data['images'] = images_data
    return data


class ArticleViewSet(viewsets.ViewSet):
    """
    處理文章的 CRUD 操作，同時處理文章圖片
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @swagger_auto_schema(
        operation_description="查詢所有文章_已發布",
        responses={200: '成功返回所有文章'}
    )
    @action(methods=['get'], detail=False, authentication_classes=[], permission_classes=[permissions.AllowAny])
    def all_active(self, request):
        queryset = Article.objects.filter(active=True).prefetch_related('images').order_by('-created_at')
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
        queryset = Article.objects.all().prefetch_related('images').order_by('-created_at')
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

        Article.objects.filter(pk=article.pk).update(view_count=F('view_count') + 1)
        article.refresh_from_db(fields=['view_count'])

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
    # [資安修補 HIGH-3] 站務文章管理僅限 staff
    @action(methods=['post'], detail=False, authentication_classes=[JWTAuthentication], permission_classes=[IsStaffPermission])
    def new(self, request):
        data = _build_article_request_data(request)
        serializer = ArticleSerializer(data=data)
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
    # [資安修補 HIGH-3] 站務文章管理僅限 staff
    @action(methods=['patch'], detail=False, authentication_classes=[JWTAuthentication], permission_classes=[IsStaffPermission])
    def change(self, request):
        try:
            pk = request.data.get("id", '')
            if pk == "":
                return Response({"msg": "id not given"}, status=status.HTTP_400_BAD_REQUEST)
            article = Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        data = _build_article_request_data(request)
        serializer = ArticleSerializer(article, data=data, partial=True)
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
    # [資安修補 HIGH-3] 站務文章管理僅限 staff
    @action(methods=['delete'], detail=False, authentication_classes=[JWTAuthentication], permission_classes=[IsStaffPermission])
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