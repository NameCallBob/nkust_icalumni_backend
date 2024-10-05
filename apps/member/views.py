from rest_framework import viewsets, status , permissions
from rest_framework.generics import ListAPIView
from django.db.models import Q

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.member.models import Member
from apps.member.serializer import MemberSerializer , MemberSimpleSerializer
from django.shortcuts import get_object_or_404

class MemberViewSet(viewsets.ViewSet):
    """
    系友會會員的 ViewSet
    提供以下功能：
    - 取得登入使用者的資料
    - 更新登入使用者的資料 (完整或部分更新)
    - 停用登入使用者的帳號
    """

    permission_classes=[permissions.IsAuthenticated]
    authentication_classes=[JWTAuthentication]

    def retrieve(self, request):
        """
        取得登入使用者的資料
        """
        member = get_object_or_404(Member, private=request.user)
        serializer = MemberSerializer(member)
        return Response(serializer.data)

    def update(self, request):
        """
        更新登入使用者的資料 (完整更新)
        """
        member = get_object_or_404(Member, private=request.user)
        serializer = MemberSerializer(member, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request):
        """
        部分更新登入使用者的資料 (PATCH)
        """
        member = get_object_or_404(Member, private=request.user)
        serializer = MemberSerializer(member, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['patch'])
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
            return Response({"message":"未知使用者"},status=404)
        except Exception as e:
            return Response({"message":f"未知錯誤:{e}"},status=500)

    @action(detail=False, methods=['patch'])
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
            return Response({"message":"未知使用者"},status=404)
        except Exception as e:
            return Response({"message":f"未知錯誤:{e}"},status=500)


class MemberListView(ListAPIView):
    """查詢會員使用"""
    serializer_class = MemberSerializer
    permission_classes=[permissions.IsAuthenticated]
    authentication_classes=[JWTAuthentication]

    def get_queryset(self):
        name = self.request.query_params.get('name', None)
        gender = self.request.query_params.get('gender', None)
        school = self.request.query_params.get('school', None)
        position = self.request.query_params.get('position', None)
        is_paid = self.request.query_params.get('is_paid', None)

        # 使用 Member 模型中已定義的 search_members 方法
        return Member.search_members(name=name, gender=gender, school=school, position=position, is_paid=is_paid)


class MemberListViewForAll(ListAPIView):
    """查詢會員使用"""
    serializer_class = MemberSimpleSerializer
    permission_classes=[permissions.AllowAny]
    authentication_classes=[JWTAuthentication]

    def get_queryset(self):
        name = self.request.query_params.get('name', None)
        intro = self.request.query_params.get('intro', None)
        position = self.request.query_params.get('position', None)

        # 使用 Member 模型中已定義的 search_members 方法
        return Member.search_members(name=name,
                                     intro=intro,
                                     position=position)