from rest_framework import viewsets, status , permissions
from rest_framework.generics import ListAPIView
from django.db.models import Q
from rest_framework.viewsets import ModelViewSet
from asgiref.sync import sync_to_async
from asgiref.sync import async_to_sync

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.record.func import create_query_log,increment_query_frequency


from apps.member.models import Member  ,OutstandingAlumni, SchoolOutstandingAlumni
from apps.member.serializer import MemberSerializer , MemberSimpleSerializer ,\
      MemberSimpleDetailSerializer , MemberSimpleAdminSerializer\
      ,OutstandingAlumniSerializer , MemberCreateSerializer, SchoolOutstandingAlumniSerializer
from django.shortcuts import get_object_or_404

from IC_alumni.permission.admin import IsAdminOrReadOnly

import random ; import string
# jwt
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from django.db import transaction

# drf_yasg
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.contrib.auth.hashers import check_password

from rest_framework.pagination import PageNumberPagination

class CustomPageNumberPagination(PageNumberPagination):
    """
    自定義分頁類別，每頁10筆資料
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
    page_query_param = 'page'
    
    def get_paginated_response(self, data):
        """
        自定義分頁響應格式
        """
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.page.paginator.per_page,
            'has_next': self.page.has_next(),
            'has_previous': self.page.has_previous(),
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })



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

    @action(methods=['get'] , detail=False , authentication_classes=[JWTAuthentication], permission_classes=[permissions.IsAuthenticated])
    def getOne(self, request):
        """
        依 id 取得會員完整資料（含個資）。
        [資安修補 CRIT-2] 原為 AllowAny，會洩漏任意會員的電話/地址/生日/Email 且可被 id 列舉。
        改為需登入；對外公開查詢請改用 /member/any/getOne/（已做 is_show 過濾）。
        """
        # [資安修補 SEC-002] 僅限本人或 staff，避免登入後以 id 列舉全會員 PII。
        member = get_object_or_404(Member, id=request.query_params.get("id",None))
        if not (request.user.is_staff or (member.private_id == request.user.id)):
            return Response({"detail": "您沒有權限查看此會員資料"}, status=status.HTTP_403_FORBIDDEN)
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
        serializer = MemberSerializer(member, data=request.data, context={'request': request})
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
        serializer = MemberSerializer(member, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="更新登入使用者的密碼",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'old_password': openapi.Schema(type=openapi.TYPE_STRING, description='舊密碼'),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='新密碼'),
            },
            required=['old_password', 'new_password']
        ),
        responses={
            200: '密碼更新成功',
            400: '請求無效',
            403: '舊密碼不正確'
        }
    )
    @action(methods=['post'], detail=False, authentication_classes=[JWTAuthentication], permission_classes=[permissions.IsAuthenticated])
    def update_password(self, request):
        """
        更新登入使用者的密碼
        """
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not check_password(old_password, user.password):
            return Response({'error': '舊密碼不正確'}, status=status.HTTP_403_FORBIDDEN)

        if old_password == new_password:
            return Response({'error': '新密碼不可與舊密碼相同'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({'message': '密碼更新成功'}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False, authentication_classes=[JWTAuthentication], permission_classes=[permissions.IsAuthenticated])
    def new(self, request):
        """
        新增會員資料
        """
        data = request.data.copy()
        data['private_input'] = request.user.id
        serializer = MemberCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MemberAnyViewSet(viewsets.ViewSet):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pagination_class = CustomPageNumberPagination()

    def __save_Record(self, request, query, type='general'):
        """
        自定義功能
        """
        ip = request.META.get('REMOTE_ADDR')
        if query == None or query == "":
            pass
        else:
            create_query_log(query=query, ip=ip, search_type=type)
            increment_query_frequency(query=query)

    @action(methods=['get'], detail=False, authentication_classes=[], permission_classes=[permissions.AllowAny])
    def getOne(self, request):
        """
        取得登入使用者的資料
        """
        query = request.query_params.get("id", None)
        member = get_object_or_404(Member, id=query)

        self.__save_Record(request, query, 'id')
        if not member.is_show:
            return Response("系友未找到", status=404)
        
        serializer = MemberSimpleDetailSerializer(member)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='get-by-grade', 
            authentication_classes=[], permission_classes=[permissions.AllowAny])
    def get_by_grade(self, request):
        """
        根據grade查詢member（支援分頁）。
        """
        grade = request.query_params.get('grade', '全部')
        query = grade
        self.__save_Record(request, query, 'grade')

        if not grade:
            return Response({'detail': '缺少年級参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 建立查詢集
        if grade == "全部" or grade == None:
            members = Member.objects.filter(is_show=True)
        else:
            members = Member.objects.filter(graduate__grade=grade, is_show=True)
        
        # 使用 select_related 優化查詢效能
        members = members.select_related('graduate', 'position').order_by('-id')
        
        # 檢查是否需要分頁
        if request.query_params.get('no_pagination') == 'true':
            serializer = MemberSimpleSerializer(members, many=True)
            return Response(serializer.data)
        
        # 應用分頁
        paginated_members = self.pagination_class.paginate_queryset(members, request)
        
        if paginated_members is not None:
            serializer = MemberSimpleSerializer(paginated_members, many=True)
            return self.pagination_class.get_paginated_response(serializer.data)
        
        # 如果分頁失敗，返回所有結果（向後兼容）
        serializer = MemberSimpleSerializer(members, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='get-by-position', 
            authentication_classes=[], permission_classes=[permissions.AllowAny])
    def get_by_position(self, request):
        """
        根據position查詢member（支援分頁）。
        """
        position = request.query_params.get('position', '')
        if position != '':
            self.__save_Record(request, position, 'position')

        # 建立查詢集
        if position == "全部" or not position:
            members = Member.objects.filter(is_show=True)
        else:
            members = Member.objects.filter(position__id=position, is_show=True)
        
        # 使用 select_related 優化查詢效能
        members = members.select_related('graduate', 'position').order_by('-id')
        
        # 檢查是否需要分頁
        if request.query_params.get('no_pagination') == 'true':
            serializer = MemberSimpleSerializer(members, many=True)
            return Response(serializer.data)
        
        # 應用分頁
        paginated_members = self.pagination_class.paginate_queryset(members, request)
        
        if paginated_members is not None:
            serializer = MemberSimpleSerializer(paginated_members, many=True)
            return self.pagination_class.get_paginated_response(serializer.data)
        
        # 如果分頁失敗，返回所有結果（向後兼容）
        serializer = MemberSimpleSerializer(members, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='alumni-search', 
            authentication_classes=[], permission_classes=[permissions.AllowAny])
    def alumni_search(self, request):
        """
        校友搜尋功能（支援分頁）
        """
        query = request.query_params.get('q', '')
        if not query:
            return Response({"detail": "請提供搜尋關鍵字。"}, status=400)
        
        self.__save_Record(request, query)
        
        # 查詢 Member 物件，並通過相關模型進行查詢
        member_results = Member.objects.filter(
            Q(name__icontains=query) |
            Q(home_phone__icontains=query) |
            Q(mobile_phone__icontains=query) |
            Q(address__icontains=query) |
            Q(intro__icontains=query) |
            Q(position__title__icontains=query) |  # 透過 Position 標題搜尋
            Q(graduate__school__icontains=query) |  # 透過 Graduate 的學校名稱搜尋
            Q(graduate__grade__icontains=query) |  # 透過 Graduate 的年級搜尋
            Q(company__name__icontains=query) |  # 透過反向關聯的公司名稱進行搜尋
            Q(company__positions__icontains=query) |  # 透過公司職位搜尋
            Q(company__description__icontains=query) |  # 透過公司簡介搜尋
            Q(company__products__icontains=query) |  # 透過公司產品搜尋
            Q(company__product_description__icontains=query) |  # 透過產品簡介搜尋
            Q(company__industry__title__icontains=query) |  # 透過產業名稱搜尋
            Q(company__industry__intro__icontains=query)  # 透過產業簡介搜尋
        )
        
        # 修正：正確套用篩選條件
        member_results = member_results.filter(is_show=True).distinct()
        
        # 使用 select_related 優化查詢效能
        member_results = member_results.select_related('graduate', 'position').order_by('-id')
        
        # 檢查是否需要分頁
        if request.query_params.get('no_pagination') == 'true':
            serializer = MemberSimpleSerializer(member_results, many=True)
            return Response(serializer.data)
        
        # 應用分頁
        paginated_members = self.pagination_class.paginate_queryset(member_results, request)
        
        if paginated_members is not None:
            serializer = MemberSimpleSerializer(paginated_members, many=True)
            return self.pagination_class.get_paginated_response(serializer.data)
        
        # 如果分頁失敗，返回所有結果（向後兼容）
        serializer = MemberSimpleSerializer(member_results, many=True)
        return Response(serializer.data)



class MemberAdminViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAdminUser]

    @action(detail=False,methods=['get'], authentication_classes=[JWTAuthentication], permission_classes=[permissions.IsAdminUser])
    def tableOutput_all(self,request):
        # [效能修補 H7] select_related 避免每列對 private/position/graduate 產生 N+1 查詢
        ob = Member.objects.all().select_related('private', 'position', 'graduate')
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
            serializer = MemberSerializer(member, data=request.data, partial=True, context={'request': request})
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
            serializer = MemberSerializer(member, data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Member.DoesNotExist:
            return Response({"error": "Member not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], authentication_classes=[JWTAuthentication], permission_classes=[permissions.IsAdminUser])
    def newUser_basic(self, request):
        """建立新使用者（全部都填）"""
        serializer = MemberSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response("ok", status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    @action(detail=False, methods=['post'], authentication_classes=[JWTAuthentication], permission_classes=[permissions.IsAdminUser])
    def newUser_email(self, request):
        """建立新使用者（僅輸入電子郵件）"""
        from apps.private.models import Private
        from apps.notice.email import email
        def generate_random_password(length=8):
            """生成8位隨機密碼"""
            characters = string.ascii_letters + string.digits
            return ''.join(random.choice(characters) for _ in range(length))

        user_email = request.data.get("email")
        user_type = request.data.get("is_superuser")
        if not user_email or not user_type:
            return Response({"error": "電子郵件沒有提供或沒說身份組"}, status=400)

        # 生成8碼隨機密碼
        password = generate_random_password()

        # 伺服器SMTP目前掛掉，此為預設密碼
        # password = "12345678"

        # 檢查使用者是否已存在
        if Private.objects.filter(email=user_email).exists():
            return Response({"error": "此帳號已建立過了"}, status=400)

        # 創建新使用者
        if user_type == "Y":
            user = Private.objects.create_superuser(email=user_email, password=password,)
        else:
            user = Private.objects.create_user(email=user_email, password=password,)

        from threading import Thread
        Thread(target=email.member_account_created,args=(user_email,password)).start()

        return Response("已為使用者建立帳號")


    @action(detail=False, methods=['delete'], authentication_classes=[JWTAuthentication], permission_classes=[permissions.IsAdminUser])
    def delete(self, request):
        """刪除使用者"""
        member_id = request.data.get('member_id')
        try:
            from apps.private.models import Private
            private_id = Member.objects.get(id=member_id).private.id
            private_ob = Private.objects.get(id=private_id)
            private_ob.delete()
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
    authentication_classes = []

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


class OutstandingAlumniViewSet(ModelViewSet):
    """
    傑出系友 API
    - 提供 CRUD 操作。
    - 所有人可查詢 `is_featured=True` 的資料。
    - 僅管理員可進行修改操作。
    """
    queryset = OutstandingAlumni.objects.select_related('member', 'member__position', 'member__graduate').all()
    serializer_class = OutstandingAlumniSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        """
        依使用者角色篩選資料：
        - 非管理員僅能看到 `is_featured=True` 的資料。
        - 管理員可看到所有資料。
        - 依照 sort_order 排序，再依照 date_awarded 排序
        """
        queryset = OutstandingAlumni.objects.select_related('member', 'member__position', 'member__graduate')
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_featured=True)
        return queryset.order_by('sort_order', '-date_awarded')

    @action(methods=["get"], detail=False, authentication_classes=[], permission_classes=[permissions.AllowAny])
    def featured(self, request):
        """
        取得所有被設為精選的傑出系友資料。
        所有使用者都可以訪問此端點。
        """
        queryset = self.queryset.filter(is_featured=True).order_by('sort_order', '-date_awarded')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=["get"], detail=False)
    def latest(self, request):
        """
        取得最新的傑出系友資料 (依建立時間排序)。
        非管理員只能看到精選資料。
        """
        queryset = self.get_queryset().order_by('-date_awarded')[:10]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=["post"], detail=True, authentication_classes=[JWTAuthentication], permission_classes=[permissions.IsAdminUser])
    def update_sort_order(self, request, pk=None):
        """
        更新排序順序
        """
        instance = self.get_object()
        sort_order = request.data.get('sort_order')
        if sort_order is not None:
            instance.sort_order = sort_order
            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return Response({"error": "sort_order is required"}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["post"], detail=False, authentication_classes=[JWTAuthentication], permission_classes=[permissions.IsAdminUser])
    def batch_update_sort_order(self, request):
        """
        批量更新排序順序
        接受格式: [{"id": 1, "sort_order": 0}, {"id": 2, "sort_order": 1}, ...]
        """
        try:
            updates = request.data
            if not isinstance(updates, list):
                return Response({"error": "Data must be a list"}, status=status.HTTP_400_BAD_REQUEST)

            for item in updates:
                if 'id' not in item or 'sort_order' not in item:
                    return Response({"error": "Each item must have 'id' and 'sort_order'"},
                                  status=status.HTTP_400_BAD_REQUEST)

            # [效能修補 L3] 改用 bulk_update，避免逐筆 save() 造成多次 UPDATE
            ids = [item['id'] for item in updates]
            objs = {o.id: o for o in OutstandingAlumni.objects.filter(id__in=ids)}
            missing = [i for i in ids if i not in objs]
            if missing:
                return Response({"error": f"Outstanding alumni with id {missing[0]} not found"},
                              status=status.HTTP_404_NOT_FOUND)
            for item in updates:
                objs[item['id']].sort_order = item['sort_order']
            with transaction.atomic():
                OutstandingAlumni.objects.bulk_update(objs.values(), ['sort_order'])

            return Response({"message": "Sort order updated successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            # [資安修補 SEC-022] 不外洩例外細節，僅回通用訊息。
            return Response({"error": "系統發生錯誤，請稍後再試"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SchoolOutstandingAlumniViewSet(ModelViewSet):
    """
    傑出校友 API
    - 提供 CRUD 操作。
    - 所有人可查詢 `is_featured=True` 的資料。
    - 僅管理員可進行修改操作。
    """
    queryset = SchoolOutstandingAlumni.objects.select_related('member', 'member__position', 'member__graduate').all()
    serializer_class = SchoolOutstandingAlumniSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        """
        依使用者角色篩選資料：
        - 非管理員僅能看到 `is_featured=True` 的資料。
        - 管理員可看到所有資料。
        - 依照 sort_order 排序，再依照 date_awarded 排序
        """
        queryset = SchoolOutstandingAlumni.objects.select_related('member', 'member__position', 'member__graduate')
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_featured=True)
        return queryset.order_by('sort_order', '-date_awarded')

    @action(methods=["get"], detail=False, authentication_classes=[], permission_classes=[permissions.AllowAny])
    def featured(self, request):
        """
        取得所有被設為精選的傑出校友資料。
        所有使用者都可以訪問此端點。
        依照 sort_order 排序
        """
        queryset = self.queryset.filter(is_featured=True).order_by('sort_order', '-date_awarded')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=["get"], detail=False)
    def latest(self, request):
        """
        取得最新的傑出校友資料 (依 date_awarded 排序)。
        非管理員只能看到精選資料。
        """
        queryset = self.get_queryset().order_by('-date_awarded')[:10]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=["post"], detail=True, authentication_classes=[JWTAuthentication], permission_classes=[permissions.IsAdminUser])
    def update_sort_order(self, request, pk=None):
        """
        更新排序順序
        """
        instance = self.get_object()
        sort_order = request.data.get('sort_order')
        if sort_order is not None:
            instance.sort_order = sort_order
            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return Response({"error": "sort_order is required"}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["post"], detail=False, authentication_classes=[JWTAuthentication], permission_classes=[permissions.IsAdminUser])
    def batch_update_sort_order(self, request):
        """
        批量更新排序順序
        接受格式: [{"id": 1, "sort_order": 0}, {"id": 2, "sort_order": 1}, ...]
        """
        try:
            updates = request.data
            if not isinstance(updates, list):
                return Response({"error": "Data must be a list"}, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                for item in updates:
                    if 'id' not in item or 'sort_order' not in item:
                        return Response({"error": "Each item must have 'id' and 'sort_order'"},
                                      status=status.HTTP_400_BAD_REQUEST)

                    try:
                        alumni = SchoolOutstandingAlumni.objects.get(id=item['id'])
                        alumni.sort_order = item['sort_order']
                        alumni.save()
                    except SchoolOutstandingAlumni.DoesNotExist:
                        return Response({"error": f"School outstanding alumni with id {item['id']} not found"},
                                      status=status.HTTP_404_NOT_FOUND)

            return Response({"message": "Sort order updated successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            # [資安修補 SEC-022] 不外洩例外細節，僅回通用訊息。
            return Response({"error": "系統發生錯誤，請稍後再試"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


