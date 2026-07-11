"""資安修補回歸測試（2026-06-28）。

涵蓋本輪修補的核心行為：
- SEC-001：會員不可經 private_input 提權為 superuser / staff。
- SEC-003：非 staff 不可竄改 is_paid / is_show；staff 可正常變更。
- SEC-002：getOne 僅本人或 staff 可取得完整個資（其他登入者 403）。

以 SQLite 測試設定執行：
    DJANGO_SETTINGS_MODULE=apps.member.test_settings \
    ./venv-alumni/bin/python manage.py test apps.member.test_security_fixes -v 2
"""
from rest_framework.test import APITestCase

from apps.member.models import Member, Position, Graduate
from apps.private.models import Private


class SecurityFixRegressionTest(APITestCase):
    def setUp(self):
        self.position = Position.objects.create(title="會員", priority=999)

        # 一般會員 A（攻擊者）
        self.user_a = Private.objects.create_user(email="a@example.com", password="Passw0rd!aA")
        self.member_a = Member.objects.create(
            private=self.user_a, name="會員A", position=self.position,
            is_paid=False, is_show=False,
        )

        # 一般會員 B（受害者）
        self.user_b = Private.objects.create_user(email="b@example.com", password="Passw0rd!bB")
        self.member_b = Member.objects.create(
            private=self.user_b, name="會員B", position=self.position,
            home_phone="0912345678", is_show=True,
        )

        # 管理員
        self.staff = Private.objects.create_superuser(email="admin@example.com", password="Passw0rd!cC")
        self.member_staff = Member.objects.create(
            private=self.staff, name="管理員", position=self.position,
        )

    # ---------------------------------------------------------------- SEC-001
    def test_sec001_member_cannot_escalate_via_private_input(self):
        """會員以 private_input 夾帶 is_superuser/is_staff 不得提權。"""
        self.client.force_authenticate(user=self.user_a)
        resp = self.client.patch("/member/logined/partial_change/", {
            "private_input": {"email": self.user_a.email, "is_superuser": True, "is_staff": True},
        }, format="json")
        self.assertIn(resp.status_code, (200, 400))
        self.user_a.refresh_from_db()
        self.assertFalse(self.user_a.is_superuser, "private_input 不得提權為 superuser")
        self.assertFalse(self.user_a.is_staff, "private_input 不得提權為 staff")

    def test_sec001_member_cannot_set_plaintext_password_via_private_input(self):
        """private_input 不得直接覆寫密碼（繞過雜湊）。"""
        self.client.force_authenticate(user=self.user_a)
        self.client.patch("/member/logined/partial_change/", {
            "private_input": {"email": self.user_a.email, "password": "plaintextpwd"},
        }, format="json")
        self.user_a.refresh_from_db()
        self.assertNotEqual(self.user_a.password, "plaintextpwd")
        self.assertFalse(self.user_a.check_password("plaintextpwd"))
        # 原密碼仍有效
        self.assertTrue(self.user_a.check_password("Passw0rd!aA"))

    # ---------------------------------------------------------------- SEC-003
    def test_sec003_member_cannot_self_set_paid_or_show(self):
        self.client.force_authenticate(user=self.user_a)
        self.client.patch("/member/logined/partial_change/", {
            "is_paid": True, "is_show": True,
        }, format="json")
        self.member_a.refresh_from_db()
        self.assertFalse(self.member_a.is_paid, "非 staff 不得自設 is_paid")
        self.assertFalse(self.member_a.is_show, "非 staff 不得自設 is_show")

    def test_sec003_staff_can_set_paid_and_show(self):
        self.client.force_authenticate(user=self.staff)
        resp = self.client.patch("/member/admin/partial_change/", {
            "member_id": self.member_a.id, "is_paid": True, "is_show": True,
        }, format="json")
        self.assertEqual(resp.status_code, 200)
        self.member_a.refresh_from_db()
        self.assertTrue(self.member_a.is_paid, "staff 應可設定 is_paid")
        self.assertTrue(self.member_a.is_show, "staff 應可設定 is_show")

    # ---------------------------------------------------------------- SEC-002
    def test_sec002_member_cannot_read_other_member_pii(self):
        self.client.force_authenticate(user=self.user_a)
        resp = self.client.get(f"/member/logined/getOne/?id={self.member_b.id}")
        self.assertEqual(resp.status_code, 403, "登入者不得讀取他人完整個資")

    def test_sec002_member_can_read_self(self):
        self.client.force_authenticate(user=self.user_a)
        resp = self.client.get(f"/member/logined/getOne/?id={self.member_a.id}")
        self.assertEqual(resp.status_code, 200)

    def test_sec002_staff_can_read_any(self):
        self.client.force_authenticate(user=self.staff)
        resp = self.client.get(f"/member/logined/getOne/?id={self.member_b.id}")
        self.assertEqual(resp.status_code, 200)
