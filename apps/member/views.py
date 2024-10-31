from rest_framework import viewsets, status , permissions
from rest_framework.generics import ListAPIView
from django.db.models import Q

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.member.models import Member , Graduate , Position
from apps.member.serializer import MemberSerializer , MemberSimpleSerializer , MemberSimpleDetailSerializer , MemberSimpleAdminSerializer
from django.shortcuts import get_object_or_404

import random ; import string
# jwt
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from django.db import transaction

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

    @action(methods=['get'] , detail=False , authentication_classes=[],permission_classes=[])
    def getOne(self, request):
        """
        取得登入使用者的資料
        """
        member = get_object_or_404(Member, id=request.query_params.get("id",None))
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

class MemberAnyViewSet(viewsets.ViewSet):

    @action(methods=['get'] , detail=False , authentication_classes=[],permission_classes=[permissions.AllowAny])
    def getOne(self, request):
        """
        取得登入使用者的資料
        """
        member = get_object_or_404(Member, id=request.query_params.get("id",None))
        serializer = MemberSimpleDetailSerializer(member)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='get-by-grade', authentication_classes=[],permission_classes=[permissions.AllowAny])
    def get_by_grade(self, request):
        """
        根據grade查詢member。
        """
        grade = request.query_params.get('grade')
        if not grade:
            return Response({'detail': '缺少 grade 参数'}, status=status.HTTP_400_BAD_REQUEST)
        if grade == "全部":
            members = Member.objects.all()
        else:
            members = Member.objects.filter(graduate__grade=grade)
        serializer = MemberSimpleSerializer(members, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='alumni-search', authentication_classes=[],permission_classes=[permissions.AllowAny])
    def alumni_search(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response({"detail": "請提供搜尋關鍵字。"}, status=400)


        # 查詢 Member 物件，並通過相關模型（Position、Graduate、Company 等）進行查詢
        member_results = Member.objects.filter(
            Q(name__icontains=query) |
            Q(home_phone__icontains=query) |
            Q(mobile_phone__icontains=query) |
            Q(address__icontains=query) |
            Q(intro__icontains=query) |
            Q(position__title__icontains=query) |  # 透過 Position 標題搜尋
            Q(graduate__school__icontains=query) |  # 透過 Graduate 的學校名稱搜尋
            Q(graduate__grade__icontains=query) |  # 透過 Graduate 的年級搜尋
            Q(member__name__icontains=query) |  # 透過反向關聯的公司名稱進行搜尋
            Q(member__positions__icontains=query) |  # 透過公司職位搜尋
            Q(member__description__icontains=query) |  # 透過公司簡介搜尋
            Q(member__products__icontains=query) |  # 透過公司產品搜尋
            Q(member__product_description__icontains=query) |  # 透過產品簡介搜尋
            Q(member__industry__title__icontains=query) |  # 透過產業名稱搜尋
            Q(member__industry__intro__icontains=query)  # 透過產業簡介搜尋
        ).distinct()  # 使用 distinct 來避免重複的結果

        # 將結果序列化並返回
        serializer = MemberSimpleSerializer(member_results, many=True)
        return Response(serializer.data)



class MemberAdminViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAdminUser]

    @action(detail=False,methods=['get'], authentication_classes=[JWTAuthentication], permission_classes=[permissions.IsAdminUser])
    def tableOutput_all(self,request):
        ob = Member.objects.all()
        serializer = MemberSimpleAdminSerializer(ob,many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], authentication_classes=[JWTAuthentication], permission_classes=[permissions.IsAdminUser])
    def getOne(self, request):
        """查詢單一使用者"""
        member_id = request.query_params.get('member_id')
        try:
            member = Member.objects.get(id=member_id)
            serializer = MemberSerializer(member)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Member.DoesNotExist:
            return Response({"error": "Member not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['patch'], authentication_classes=[JWTAuthentication], permission_classes=[permissions.IsAdminUser])
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

    @action(detail=False, methods=['put'], authentication_classes=[JWTAuthentication], permission_classes=[permissions.IsAdminUser])
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

    @action(detail=False, methods=['post'], authentication_classes=[JWTAuthentication], permission_classes=[permissions.IsAdminUser])
    def newUser_basic(self, request):
        """建立新使用者（全部都填）"""
        serializer = MemberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    @action(detail=False, methods=['post'], authentication_classes=[JWTAuthentication], permission_classes=[permissions.IsAuthenticated])
    def newUser_email(self, request):
        """建立新使用者（僅輸入電子郵件）"""
        from apps.private.models import Private
        from apps.notice.email import email
        def generate_random_password(length=8):
            """生成8位隨機密碼"""
            characters = string.ascii_letters + string.digits
            return ''.join(random.choice(characters) for _ in range(length))

        user_email = request.data.get("email")

        if not user_email:
            return Response({"error": "Email is required."}, status=400)

        # 生成8碼隨機密碼
        password = generate_random_password()

        # 檢查使用者是否已存在
        if Private.objects.filter(email=user_email).exists():
            return Response({"error": "User with this email already exists."}, status=400)

        # 創建新使用者
        user = Private.objects.create_user(email=user_email, password=password,)
        from threading import Thread
        Thread(target=email.member_account_created,args=(user_email,password)).start()

        return Response("已為使用者建立帳號")


    @action(detail=False, methods=['delete'], authentication_classes=[JWTAuthentication], permission_classes=[permissions.IsAdminUser])
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
    @action(detail=False, methods=['patch'], authentication_classes=[JWTAuthentication], permission_classes=[permissions.IsAdminUser])
    def switch_active(self, request):
        """
        停用登入使用者的帳號 (將 is_active 設為 False)
        並註銷該用戶的所有 Token
        """
        try:
            member_id = request.data.get("member_id")
            with transaction.atomic():  # 使用事務來包裹多個操作
                ob = Member.objects.select_for_update().get(id=member_id)

                # 切換 is_active 狀態
                ob.private.is_active = not ob.private.is_active
                ob.private.save()

                # 找到該用戶的所有 Outstanding Tokens 並將它們加入黑名單
                tokens = OutstandingToken.objects.filter(user=ob.private)
                for token in tokens:
                    # 將每個 Token 加入黑名單
                    BlacklistedToken.objects.get_or_create(token=token)

            return Response("帳號狀態已切換並登出所有 token", status=status.HTTP_200_OK)
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
    @action(detail=False, methods=['patch'], authentication_classes=[JWTAuthentication], permission_classes=[permissions.IsAdminUser])
    def switch_paid(self, request):
        """
        因未繳費關閉帳號及記錄
        並註銷該會員所有 Token
        """
        try:
            member_id = request.data.get("member_id")
            with transaction.atomic():  # 使用事務來包裹多個操作，保證數據一致性
                ob = Member.objects.select_for_update().get(id=member_id)

                # 切換 is_paid 和 is_active 狀態
                ob.is_paid = not ob.is_paid
                ob.private.is_active = not ob.private.is_active
                ob.private.save()
                ob.save()

                # 找到該用戶的所有 Outstanding Tokens 並將它們加入黑名單
                tokens = OutstandingToken.objects.filter(user=ob.private)
                for token in tokens:
                    BlacklistedToken.objects.get_or_create(token=token)

            return Response({'status': 'account deactivated and all tokens blacklisted'}, status=status.HTTP_200_OK)
        except Member.DoesNotExist:
            return Response({"message": "未知使用者"}, status=404)
        except Exception as e:
            return Response({"message": f"未知錯誤: {e}"}, status=500)

    @action(detail=False, methods=['patch'], authentication_classes=[JWTAuthentication], permission_classes=[permissions.IsAdminUser])
    def update_password(self, request):
        """
        因未繳費關閉帳號及記錄
        """
        try:
            member_id = request.data.get("member_id")
            password = request.data.get("password")
            ob = Member.objects.get(id=member_id)

            ob.private.set_password(password)  # Properly set the hashed password
            ob.private.save()  # Save the private object

            return Response({'status': 'password updated'}, status=status.HTTP_200_OK)
        except Member.DoesNotExist:
            return Response({"message": "未知使用者"}, status=404)
        except Exception as e:
            return Response({"message": f"未知錯誤: {e}"}, status=500)

class MemberListView(ListAPIView):
    """查詢會員使用"""
    serializer_class = MemberSerializer
    permission_classes = [permissions.IsAdminUser]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_description="查詢會員資料",
        manual_parameters=[
            openapi.Parameter('name', openapi.IN_QUERY, description="會員名稱", type=openapi.TYPE_STRING),
            openapi.Parameter('gender', openapi.IN_QUERY, description="性別", type=openapi.TYPE_STRING),
            openapi.Parameter('school', openapi.IN_QUERY, description="畢業學校", type=openapi.TYPE_STRING),
            openapi.Parameter('position', openapi.IN_QUERY, description="職位", type=openapi.TYPE_STRING),
            openapi.Parameter('is_paid', openapi.IN_QUERY, description="是否已繳費", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('search', openapi.IN_QUERY, description="全域搜尋關鍵字", type=openapi.TYPE_STRING),
        ],
        responses={200: '成功返回會員資料'}
    )
    def get_queryset(self):
        # 若為ＩＤ查詢
        id = self.request.query_params.get('id', None)
        if id:
            return Member.objects.filter(id=id)

        # 獲取查詢參數
        name = self.request.query_params.get('name', None)
        gender = self.request.query_params.get('gender', None)
        school = self.request.query_params.get('school', None)
        position = self.request.query_params.get('position', None)
        is_paid = self.request.query_params.get('is_paid', None)
        search = self.request.query_params.get('search', None)
        is_active = self.request.query_params.get('is_active', None)
        # 將 is_paid 字串轉換成布林值
        if is_paid is not None:
            if is_paid.lower() == 'true':
                is_paid = True
            elif is_paid.lower() == 'false':
                is_paid = False
            else:
                is_paid = None
        # 將 is_active 字串轉換成布林值
        if is_active is not None:
            if is_active.lower() == 'true':
                is_active = True
            elif is_active.lower() == 'false':
                is_active = False
            else:
                is_active = None
        # 執行搜尋，包含search和其他條件的聯合篩選
        return Member.search_members(name=name, gender=gender, school=school,
                                     position=position, is_paid=is_paid, search=search ,
                                     is_active=is_active)


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