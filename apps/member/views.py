from rest_framework import viewsets, status , permissions
from rest_framework.generics import ListAPIView
from django.db.models import Q

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.member.models import Member
from apps.member.serializer import MemberSerializer , MemberSimpleSerializer
from django.shortcuts import get_object_or_404

import random ; import string

# drf_yasg
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class MemberViewSet(viewsets.ViewSet):
    """
    系友會「自身」會員的 ViewSet
    提供以下功能：
    - 取得登入使用者的資料
    - 更新登入使用者的資料 (完整或部分更新)
    - 停用登入使用者的帳號
    """

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_description="取得登入使用者的資料",
        responses={200: '成功返回使用者資料'}
    )
    @action(methods=['get'] , detail=False , authentication_classes=[JWTAuthentication],permission_classes=[permissions.IsAuthenticated])
    def selfInfo(self, request):
        """
        取得登入使用者的資料
        """
        member = get_object_or_404(Member, private=request.user)
        serializer = MemberSerializer(member)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="更新登入使用者的資料 (完整更新)",
        request_body=MemberSerializer,
        responses={
            200: '更新成功',
            400: '請求無效'
        }
    )
    @action(methods=['post'] , detail=False , authentication_classes=[JWTAuthentication],permission_classes=[permissions.IsAuthenticated])
    def change(self, request):
        """
        更新登入使用者的資料 (完整更新)
        """
        member = get_object_or_404(Member, private=request.user)
        serializer = MemberSerializer(member, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="部分更新登入使用者的資料 (PATCH)",
        request_body=MemberSerializer,
        responses={
            200: '更新成功',
            400: '請求無效'
        }
    )
    @action(methods=['patch'] , detail=False , authentication_classes=[JWTAuthentication],permission_classes=[permissions.IsAuthenticated])
    def partial_change(self, request):
        """
        部分更新登入使用者的資料 (PATCH)
        """
        member = get_object_or_404(Member, private=request.user)
        serializer = MemberSerializer(member, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MemberAdminViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAdminUser]

    @action(detail=False, methods=['get'], authentication_classes=[JWTAuthentication], permission_classes=[permissions.IsAuthenticated])
    def getOne(self, request):
        """查詢單一使用者"""
        member_id = request.query_params.get('member_id')
        try:
            member = Member.objects.get(id=member_id)
            serializer = MemberSerializer(member)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Member.DoesNotExist:
            return Response({"error": "Member not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['patch'], authentication_classes=[JWTAuthentication], permission_classes=[permissions.IsAuthenticated])
    def partial_change(self, request):
        """修改部分使用者資料"""
        member_id = request.data.get('member_id')
        try:
            member = Member.objects.get(id=member_id)
            serializer = MemberSerializer(member, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Member.DoesNotExist:
            return Response({"error": "Member not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['put'], authentication_classes=[JWTAuthentication], permission_classes=[permissions.IsAuthenticated])
    def change(self, request):
        """修改使用者資料"""
        member_id = request.data.get('member_id')
        try:
            member = Member.objects.get(id=member_id)
            serializer = MemberSerializer(member, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Member.DoesNotExist:
            return Response({"error": "Member not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], authentication_classes=[JWTAuthentication], permission_classes=[permissions.IsAuthenticated])
    def newUser_basic(self, request):
        """建立新使用者（全部都填）"""
        serializer = MemberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['delete'], authentication_classes=[JWTAuthentication], permission_classes=[permissions.IsAuthenticated])
    def delete(self, request):
        """刪除使用者"""
        member_id = request.data.get('member_id')
        try:
            member = Member.objects.get(id=member_id)
            member.delete()
            return Response({"message": "Member deleted"}, status=status.HTTP_200_OK)
        except Member.DoesNotExist:
            return Response({"error": "Member not found"}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="停用登入使用者的帳號 (將 is_active 設為 False)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'member_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='會員 ID'),
            },
            required=['member_id']
        ),
        responses={
            200: '帳號停用成功',
            404: '使用者不存在'
        }
    )
    @action(detail=False, methods=['patch'] , authentication_classes=[JWTAuthentication],permission_classes=[permissions.IsAuthenticated])
    def switch_active(self, request):
        """
        停用登入使用者的帳號 (將 is_active 設為 False)
        """
        try:
            member_id = request.data.get("member_id")
            ob = Member.objects.get(id=member_id)
            ob.private.is_active = not ob.private.is_active
            ob.save()
        except Member.DoesNotExist:
            return Response({"message": "未知使用者"}, status=404)
        except Exception as e:
            return Response({"message": f"未知錯誤: {e}"}, status=500)

    @swagger_auto_schema(
        operation_description="因未繳費關閉帳號及記錄",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'member_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='會員 ID'),
            },
            required=['member_id']
        ),
        responses={
            200: '帳號關閉成功',
            404: '使用者不存在'
        }
    )
    @action(detail=False, methods=['patch'] , authentication_classes=[JWTAuthentication],permission_classes=[permissions.IsAuthenticated])
    def switch_paid(self, request):
        """
        因未繳費關閉帳號及記錄
        """
        try:
            member_id = request.data.get("member_id")
            ob = Member.objects.get(id=member_id)
            ob.is_paid = not ob.is_paid
            ob.private.is_active = not ob.private.is_active
            ob.save()
            return Response({'status': 'account deactivated'}, status=status.HTTP_200_OK)
        except Member.DoesNotExist:
            return Response({"message": "未知使用者"}, status=404)
        except Exception as e:
            return Response({"message": f"未知錯誤: {e}"}, status=500)


class MemberListView(ListAPIView):
    """查詢會員使用"""
    serializer_class = MemberSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_description="查詢會員資料",
        manual_parameters=[
            openapi.Parameter('name', openapi.IN_QUERY, description="會員名稱", type=openapi.TYPE_STRING),
            openapi.Parameter('gender', openapi.IN_QUERY, description="性別", type=openapi.TYPE_STRING),
            openapi.Parameter('school', openapi.IN_QUERY, description="畢業學校", type=openapi.TYPE_STRING),
            openapi.Parameter('position', openapi.IN_QUERY, description="職位", type=openapi.TYPE_STRING),
            openapi.Parameter('is_paid', openapi.IN_QUERY, description="是否已繳費", type=openapi.TYPE_BOOLEAN),
        ],
        responses={200: '成功返回會員資料'}
    )
    def get_queryset(self):
        # 若為ＩＤ查詢
        id = self.request.query_params.get('id', None)
        if id:
            return Member.objects.get(id=id)
        name = self.request.query_params.get('name', None)
        gender = self.request.query_params.get('gender', None)
        school = self.request.query_params.get('school', None)
        position = self.request.query_params.get('position', None)
        is_paid = self.request.query_params.get('is_paid', None)

        return Member.search_members(name=name, gender=gender, school=school, position=position, is_paid=is_paid)


class MemberListViewForAll(ListAPIView):
    """查詢會員使用"""
    serializer_class = MemberSimpleSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_description="查詢所有會員的資料",
        manual_parameters=[
            openapi.Parameter('name', openapi.IN_QUERY, description="會員名稱", type=openapi.TYPE_STRING),
            openapi.Parameter('intro', openapi.IN_QUERY, description="簡介", type=openapi.TYPE_STRING),
            openapi.Parameter('position', openapi.IN_QUERY, description="職位", type=openapi.TYPE_STRING),
        ],
        responses={200: '成功返回會員資料'}
    )
    def get_queryset(self):
        name = self.request.query_params.get('name', None)
        intro = self.request.query_params.get('intro', None)
        position = self.request.query_params.get('position', None)

        return Member.search_members(name=name, intro=intro, position=position)