from rest_framework import viewsets, status , permissions
from rest_framework.decorators import action , authentication_classes , permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from apps.article.models import Article
from apps.article.serializer import ArticleSerializer

class ArticleViewSet(viewsets.ViewSet):
    """
    處理文章的 CRUD 操作，同時處理文章圖片
    """

    # 查詢所有文章
    @action(methods=['get'],detail=False,authentication_classes=[],permission_classes=[permissions.AllowAny])
    def all(self, request):
        queryset = Article.objects.all()
        serializer = ArticleSerializer(queryset, many=True)
        return Response(serializer.data)

    # 查詢單一文章
    @action(methods=['get'],detail=False,authentication_classes=[],permission_classes=[permissions.AllowAny])
    def get_one(self, request, pk=None):
        try:
            article = Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        # 增加查看次數
        article.view_count += 1
        article.save()

        serializer = ArticleSerializer(article)
        return Response(serializer.data)

    # 創建文章和圖片
    @action(methods=['post'],detail=False,authentication_classes=[JWTAuthentication],permission_classes=[permissions.IsAuthenticated])
    def new(self, request):
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 更新文章和圖片
    @action(methods=['patch'],detail=False,authentication_classes=[JWTAuthentication],permission_classes=[permissions.IsAuthenticated])
    def change(self, request, pk=None):
        try:
            article = Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ArticleSerializer(article, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 刪除文章
    @action(methods=['delete'],detail=False,authentication_classes=[JWTAuthentication],permission_classes=[permissions.IsAuthenticated])
    def delete(self, request, pk=None):
        try:
            article = Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
