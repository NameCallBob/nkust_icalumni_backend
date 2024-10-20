# views.py
from rest_framework import viewsets, status , permissions
from rest_framework.response import Response
from rest_framework.decorators import action , authentication_classes , permission_classes
from apps.member.models import Position, Graduate
from apps.member.serializer import PositionSerializer, GraduateSerializer
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.authentication import JWTAuthentication

class PositionViewSet(viewsets.ViewSet):
    """
    
    """

    @action(detail=False, methods=['get'], url_path='get-all' ,authentication_classes=[],permission_classes=[permissions.AllowAny])
    def get_all(self, request):
        queryset = Position.objects.all()
        serializer = PositionSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='create-new',authentication_classes=[JWTAuthentication],permission_classes=[permissions.IsAuthenticated])
    def create_new(self, request):
        serializer = PositionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='get-one',authentication_classes=[],permission_classes=[permissions.AllowAny])
    def get_one(self, request):
        id = request.query_params.get('id')
        if not id:
            return Response({'detail': '缺少 id 参数'}, status=status.HTTP_400_BAD_REQUEST)
        position = get_object_or_404(Position, id=id)
        serializer = PositionSerializer(position)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='replace',authentication_classes=[JWTAuthentication],permission_classes=[permissions.IsAuthenticated])
    def replace(self, request):
        # 不使用 pk，而是从请求数据中获取 id
        id = request.data.get('id')
        if not id:
            return Response({'detail': '缺少 id 字段'}, status=status.HTTP_400_BAD_REQUEST)
        position = get_object_or_404(Position, id=id)
        serializer = PositionSerializer(position, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='modify',authentication_classes=[JWTAuthentication],permission_classes=[permissions.IsAuthenticated])
    def modify(self, request):
        id = request.data.get('id')
        if not id:
            return Response({'detail': '缺少 id 字段'}, status=status.HTTP_400_BAD_REQUEST)
        position = get_object_or_404(Position, id=id)
        serializer = PositionSerializer(position, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='remove',authentication_classes=[JWTAuthentication],permission_classes=[permissions.IsAuthenticated])
    def remove(self, request):
        id = request.data.get('id')
        if not id:
            return Response({'detail': '缺少 id 字段'}, status=status.HTTP_400_BAD_REQUEST)
        position = get_object_or_404(Position, id=id)
        position.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class GraduateViewSet(viewsets.ViewSet):
    """

    """
    @action(detail=False, methods=['get'], url_path='unique-grades',authentication_classes=[],permission_classes=[permissions.AllowAny])
    def get_unique_grades(self, request):
        """

        """
        grades = Graduate.objects.values_list('grade', flat=True).distinct()
        return Response(grades)

    @action(detail=False, methods=['get'], url_path='get-all',authentication_classes=[],permission_classes=[permissions.AllowAny])
    def get_all(self, request):
        queryset = Graduate.objects.all()
        serializer = GraduateSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='create-new',authentication_classes=[JWTAuthentication],permission_classes=[permissions.IsAuthenticated])
    def create_new(self, request):
        serializer = GraduateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='get-one',authentication_classes=[],permission_classes=[permissions.AllowAny])
    def get_one(self, request):
        id = request.query_params.get('id')
        if not id:
            return Response({'detail': '缺少 id 参数'}, status=status.HTTP_400_BAD_REQUEST)
        graduate = get_object_or_404(Graduate, id=id)
        serializer = GraduateSerializer(graduate)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='replace',authentication_classes=[JWTAuthentication],permission_classes=[permissions.IsAuthenticated])
    def replace(self, request):
        id = request.data.get('id')
        if not id:
            return Response({'detail': '缺少 id 字段'}, status=status.HTTP_400_BAD_REQUEST)
        graduate = get_object_or_404(Graduate, id=id)
        serializer = GraduateSerializer(graduate, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='modify',authentication_classes=[JWTAuthentication],permission_classes=[permissions.IsAuthenticated])
    def modify(self, request):
        id = request.data.get('id')
        if not id:
            return Response({'detail': '缺少 id 字段'}, status=status.HTTP_400_BAD_REQUEST)
        graduate = get_object_or_404(Graduate, id=id)
        serializer = GraduateSerializer(graduate, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='remove')
    def remove(self, request):
        id = request.data.get('id')
        if not id:
            return Response({'detail': '缺少 id 字段'}, status=status.HTTP_400_BAD_REQUEST)
        graduate = get_object_or_404(Graduate, id=id)
        graduate.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
