from django.test import TestCase
from rest_framework.test import APITestCase
from apps.member.models import Member, Position, Graduate
from apps.member.serializer import MemberSimpleDetailSerializer
from apps.company.models import Company, Industry
from apps.private.models import Private
from django.contrib.auth import get_user_model


class MemberSimpleDetailSerializerTest(TestCase):
    """測試 MemberSimpleDetailSerializer"""

    def setUp(self):
        """設置測試資料"""
        # 建立測試用的 Position
        self.position = Position.objects.create(
            title="測試職位",
            priority=1
        )

        # 建立測試用的 Graduate
        self.graduate = Graduate.objects.create(
            school="測試大學",
            grade="110"
        )

        # 建立測試用的 Private (用戶)
        self.private = Private.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )

        # 建立測試用的 Member
        self.member = Member.objects.create(
            private=self.private,
            name="測試會員",
            gender="M",
            intro="這是測試介紹",
            position=self.position,
            graduate=self.graduate,
            is_show=True
        )

        # 建立測試用的 Industry
        self.industry = Industry.objects.create(
            title="測試產業"
        )

        # 建立測試用的 Company
        self.company = Company.objects.create(
            name="測試公司",
            member=self.member,
            industry=self.industry,
            positions="測試職位",
            description="測試公司描述"
        )

    def test_serializer_with_complete_data(self):
        """測試序列化器能正確處理完整資料"""
        serializer = MemberSimpleDetailSerializer(self.member)
        data = serializer.data

        # 檢查基本欄位
        self.assertEqual(data['name'], '測試會員')
        self.assertEqual(data['gender'], 'M')
        self.assertEqual(data['intro'], '這是測試介紹')

        # 檢查 position
        self.assertIsNotNone(data['position'])
        self.assertEqual(data['position']['title'], '測試職位')

        # 檢查 graduate
        self.assertIsNotNone(data['graduate'])
        self.assertEqual(data['graduate']['school'], '測試大學')
        self.assertEqual(data['graduate']['grade'], '110')

        # 檢查 company
        self.assertIsNotNone(data['company'])
        self.assertEqual(data['company']['name'], '測試公司')

    def test_serializer_without_company(self):
        """測試沒有公司資料的會員"""
        # 建立一個沒有公司的會員
        member_no_company = Member.objects.create(
            name="無公司會員",
            gender="F",
            is_show=True
        )

        serializer = MemberSimpleDetailSerializer(member_no_company)
        data = serializer.data

        self.assertEqual(data['name'], '無公司會員')
        self.assertEqual(data['gender'], 'F')
        self.assertIsNone(data['company'])
        self.assertIsNone(data['position'])
        self.assertIsNone(data['graduate'])

    def test_serializer_with_null_fields(self):
        """測試處理空值欄位"""
        # 建立只有必填欄位的會員
        minimal_member = Member.objects.create(
            name="最小會員",
            is_show=True
        )

        serializer = MemberSimpleDetailSerializer(minimal_member)
        data = serializer.data

        self.assertEqual(data['name'], '最小會員')
        self.assertIsNone(data['gender'])
        self.assertIsNone(data['intro'])  # intro 欄位允許為 None
        self.assertIsNone(data['company'])
        self.assertEqual(data['self_images'], [])
        self.assertIsNone(data['company_images'])


class MemberAnyViewSetTest(APITestCase):
    """測試 MemberAnyViewSet 的 getOne API"""

    def setUp(self):
        """設置測試資料"""
        # 建立測試用的 Graduate
        self.graduate = Graduate.objects.create(
            school="國立高雄科技大學",
            grade="110"
        )

        # 建立測試用的 Position
        self.position = Position.objects.create(
            title="財務長",
            priority=1
        )

        # 建立測試會員
        self.member = Member.objects.create(
            name="測試系友",
            gender="F",
            position=self.position,
            graduate=self.graduate,
            is_show=True
        )

    def test_getOne_success(self):
        """測試成功取得會員資料"""
        response = self.client.get(f'/member/any/getOne/?id={self.member.id}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], '測試系友')
        self.assertEqual(response.data['gender'], 'F')
        self.assertIsNotNone(response.data['position'])
        self.assertEqual(response.data['position']['title'], '財務長')
        self.assertIsNotNone(response.data['graduate'])
        self.assertEqual(response.data['graduate']['school'], '國立高雄科技大學')

    def test_getOne_member_not_found(self):
        """測試查詢不存在的會員"""
        response = self.client.get('/member/any/getOne/?id=99999')
        self.assertEqual(response.status_code, 404)

    def test_getOne_member_not_shown(self):
        """測試查詢 is_show=False 的會員"""
        hidden_member = Member.objects.create(
            name="隱藏會員",
            is_show=False
        )

        response = self.client.get(f'/member/any/getOne/?id={hidden_member.id}')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, "系友未找到")

    def test_getOne_without_id(self):
        """測試沒有提供 ID 參數"""
        response = self.client.get('/member/any/getOne/')
        self.assertEqual(response.status_code, 404)