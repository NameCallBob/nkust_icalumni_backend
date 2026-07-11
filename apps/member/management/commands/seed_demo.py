"""
種子資料（demo seed）管理命令。

用途：在全新（或測試）環境快速建立一組具代表性的資料，方便驗證原有功能。
特性：
  - 具冪等性（idempotent）：以 get_or_create / update_or_create 為主，可重複執行。
  - 不寄送任何 Email：執行期間將帳號建立信件改為 no-op，避免背景執行緒卡住。

使用：
    python manage.py seed_demo
    python manage.py seed_demo --flush   # 先清空 demo 範圍資料再重建
"""
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone


class Command(BaseCommand):
    help = "建立 demo / 測試用種子資料（具冪等性，不寄信）"

    # [資安修補 SEC-029] demo 密碼改由環境變數覆寫，避免固定弱密碼成為已知後門。
    import os as _os
    DEMO_PASSWORD = _os.getenv("SEED_DEMO_PASSWORD", "Demo#1234")

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="先刪除 demo 範圍的資料再重新建立",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="允許在 DEBUG=False（疑似正式）環境執行（預設禁止）",
        )

    def handle(self, *args, **options):
        # [資安修補 SEC-029] 預設禁止在非 DEBUG（疑似正式）環境執行，避免建立已知 demo 管理員後門。
        from django.conf import settings as _settings
        if not getattr(_settings, "DEBUG", False) and not options.get("force") \
                and __import__("os").getenv("ALLOW_SEED_DEMO", "0") != "1":
            self.stderr.write(self.style.ERROR(
                "拒絕執行：偵測到非 DEBUG 環境。如確需執行請加 --force 或設定 ALLOW_SEED_DEMO=1。"))
            return

        # 1) 關閉帳號建立信件，避免 SMTP 背景執行緒卡住程序
        from apps.notice import email as email_module
        email_module.email.member_account_created = staticmethod(lambda *a, **k: None)

        with transaction.atomic():
            if options["flush"]:
                self._flush()
            self._seed()

        self.stdout.write(self.style.SUCCESS("✅ 種子資料建立完成"))
        self.stdout.write(f"   管理員帳號: admin@demo.local / {self.DEMO_PASSWORD}")
        self.stdout.write(f"   一般會員帳號: alice@demo.local ~ / {self.DEMO_PASSWORD}")

    # ------------------------------------------------------------------ flush
    def _flush(self):
        from apps.private.models import Private
        from apps.member.models import (
            Member, Graduate, Position, OutstandingAlumni, SchoolOutstandingAlumni,
        )
        from apps.company.models import Company, Industry
        from apps.product.models import Product, ProductCate
        from apps.article.models import Article
        from apps.recruit.models import Recruit
        from apps.picture.models import SlideImage, PopupAd

        self.stdout.write("🧹 清除 demo 範圍資料 ...")
        Private.objects.filter(email__endswith="@demo.local").delete()  # 連帶 Member/Company...
        OutstandingAlumni.objects.all().delete()
        SchoolOutstandingAlumni.objects.all().delete()
        Article.objects.filter(title__startswith="[Demo]").delete()
        Recruit.objects.filter(title__startswith="[Demo]").delete()
        SlideImage.objects.filter(title__startswith="[Demo]").delete()
        PopupAd.objects.all().delete()
        Member.objects.filter(name__startswith="Demo").delete()

    # ------------------------------------------------------------------- seed
    def _seed(self):
        from apps.private.models import Private
        from apps.member.models import (
            Member, Graduate, Position, OutstandingAlumni, SchoolOutstandingAlumni,
        )
        from apps.company.models import Company, Industry
        from apps.product.models import Product, ProductCate, ProductImage
        from apps.article.models import Article, ArticleImage
        from apps.recruit.models import Recruit, Contact
        from apps.picture.models import SlideImage, PopupAd
        from apps.notice.models import Notice
        from apps.Info.models import (
            AlumniAssociation, Constitution, OrganizationalStructure,
            MembershipRequirement, MembershipRequirement_v2,
        )

        pwd = self.DEMO_PASSWORD

        # --- 帳號（管理員 + 一般使用者） ---
        admin, created = Private.objects.get_or_create(
            email="admin@demo.local",
            defaults={"is_staff": True, "is_superuser": True, "is_active": True},
        )
        if created:
            admin.set_password(pwd)
            admin.save()

        # --- 職位 ---
        positions = {}
        for title, pri in [("理事長", 1), ("副理事長", 2), ("秘書長", 3), ("一般會員", 99)]:
            positions[title] = Position.objects.get_or_create(title=title, defaults={"priority": pri})[0]

        # --- 產業別 ---
        industries = {}
        for name in ["資訊科技", "金融服務", "製造業", "零售貿易"]:
            industries[name] = Industry.objects.get_or_create(
                title=name, defaults={"intro": f"{name}相關產業"}
            )[0]

        # --- 會員（含帳號 / 畢業資料 / 公司 / 產品 / 通知設定） ---
        people = [
            ("Alice Wang", "alice", "F", "理事長", "110", "資訊科技", True),
            ("Bob Chen", "bob", "M", "副理事長", "111", "金融服務", True),
            ("Carol Lin", "carol", "F", "秘書長", "112", "製造業", True),
            ("David Wu", "david", "M", "一般會員", "113", "零售貿易", False),
            ("Eve Huang", "eve", "F", "一般會員", "114", "資訊科技", True),
        ]
        members = {}
        for full_name, handle, gender, pos, grade, ind, is_show in people:
            acc, acc_created = Private.objects.get_or_create(
                email=f"{handle}@demo.local",
                defaults={"is_active": True},
            )
            if acc_created:
                acc.set_password(pwd)
                acc.save()

            grad, _ = Graduate.objects.get_or_create(
                student_id=f"C{grade}156{handle[:3]}",
                defaults={"grade": grade},
            )
            member, _ = Member.objects.update_or_create(
                private=acc,
                defaults={
                    "graduate": grad,
                    "position": positions[pos],
                    "name": full_name,
                    "home_phone": "07-1234567",
                    "mobile_phone": f"09{grade}123456"[:15],
                    "gender": gender,
                    "address": "高雄市三民區建工路415號",
                    "is_paid": True,
                    "intro": f"{full_name} 是智慧商務系 {grade} 級系友。",
                    "birth_date": date(1995, 1, 1),
                    "is_show": is_show,
                },
            )
            members[handle] = member

            Notice.objects.get_or_create(member=member)

            # 公司（每位會員一間）
            company, _ = Company.objects.update_or_create(
                member=member,
                defaults={
                    "industry": industries[ind],
                    "name": f"{full_name} 科技有限公司",
                    "positions": "負責人",
                    "description": f"{ind}領域的創新公司。",
                    "products": "顧問服務",
                    "product_description": "提供專業顧問與解決方案。",
                    "website": "https://example.com",
                    "address": "高雄市前鎮區成功二路25號",
                    "email": f"{handle}@company.demo.local",
                    "phone_number": "07-7654321",
                },
            )

            # 產品分類 + 產品
            cate, _ = ProductCate.objects.get_or_create(company=company, name="主力產品")
            Product.objects.get_or_create(
                company=company, category=cate, name=f"{full_name} 旗艦方案",
                defaults={"description": "旗艦級產品方案。", "is_active": True},
            )

        # --- 傑出系友（OutstandingAlumni）— 系上層級 ---
        oa_targets = [("alice", True, "2024 年度傑出系友", 1),
                      ("bob", True, "創業楷模", 2),
                      ("carol", False, "產學貢獻", 3)]
        for handle, feat, hl, order in oa_targets:
            OutstandingAlumni.objects.update_or_create(
                member=members[handle],
                defaults={
                    "achievements": f"{members[handle].name} 在專業領域有卓越貢獻。",
                    "is_featured": feat,
                    "highlight": hl,
                    "date_awarded": date(2024, 1, 15),
                    "sort_order": order,
                },
            )

        # --- 傑出校友（SchoolOutstandingAlumni）— 校級 ---
        soa_targets = [("alice", True, "校級傑出校友 - 金融科技創新", 1),
                       ("eve", True, "校級傑出校友 - AI 應用", 2),
                       ("david", False, "校級傑出校友 - 社會貢獻", 3)]
        for handle, feat, hl, order in soa_targets:
            SchoolOutstandingAlumni.objects.update_or_create(
                member=members[handle],
                defaults={
                    "achievements": f"{members[handle].name} 為母校爭光。",
                    "is_featured": feat,
                    "highlight": hl,
                    "date_awarded": date(2024, 6, 1),
                    "sort_order": order,
                },
            )

        # --- 文章 ---
        for i in range(1, 4):
            Article.objects.update_or_create(
                title=f"[Demo] 系友會公告第 {i} 號",
                defaults={
                    "content": f"<p>這是第 {i} 篇 demo 公告內容。</p>",
                    "active": True,
                    "publish_at": timezone.now(),
                    "expire_at": timezone.now() + timedelta(days=90),
                    "view_count": i * 10,
                },
            )

        # --- 招募 ---
        first_company = members["alice"].company
        recruit, _ = Recruit.objects.update_or_create(
            title="[Demo] 後端工程師",
            defaults={
                "company": first_company,
                "intro": "<p>招募後端工程師，熟悉 Django。</p>",
                "deadline": date.today() + timedelta(days=30),
                "active": True,
            },
        )
        Contact.objects.get_or_create(
            recruit=recruit,
            defaults={
                "company_name": first_company.name,
                "name": "人資部",
                "phone": "07-7654321",
                "email": "hr@company.demo.local",
            },
        )

        # --- 輪播圖 / 彈窗廣告（不含實體圖檔，僅資料） ---
        for i in range(1, 4):
            SlideImage.objects.update_or_create(
                title=f"[Demo] 輪播 {i}",
                defaults={
                    "type": "home",
                    "description": "首頁輪播",
                    "link_url": "https://example.com",
                    "priority": i,
                    "active": True,
                },
            )

        # --- 系友會資訊內容（Info） ---
        AlumniAssociation.objects.get_or_create(
            defaults={"description": "<p>智慧商務系系友會簡介。</p>"}
        ) if not AlumniAssociation.objects.exists() else None
        Constitution.objects.get_or_create(
            defaults={"description": "<p>系友會章程內容。</p>"}
        ) if not Constitution.objects.exists() else None
        OrganizationalStructure.objects.get_or_create(
            defaults={"description": "<p>組織架構說明。</p>"}
        ) if not OrganizationalStructure.objects.exists() else None
        MembershipRequirement.objects.get_or_create(
            defaults={"description": "<p>入會需求（舊版）。</p>"}
        ) if not MembershipRequirement.objects.exists() else None
        MembershipRequirement_v2.objects.get_or_create(
            defaults={"description": "<p>入會需求（v2）：請填寫申請表並繳交會費。</p>"}
        ) if not MembershipRequirement_v2.objects.exists() else None

        self.stdout.write(
            f"   會員 {Member.objects.count()} 筆 / 公司 {Company.objects.count()} 筆 / "
            f"傑出系友 {OutstandingAlumni.objects.count()} 筆 / "
            f"傑出校友 {SchoolOutstandingAlumni.objects.count()} 筆"
        )
