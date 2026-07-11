from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.utils import timezone
from django.utils.text import slugify
from apps.company.models import Company
from apps.recruit.models import Recruit
from apps.article.models import Article
from apps.member.models import Member
from datetime import datetime
import json

class DynamicSitemapView(APIView):
    """動態生成網站地圖 XML"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        base_url = "https://nkusticalumni.org"
        urls = []

        # 靜態頁面
        static_pages = [
            {"loc": "/", "priority": 1.0, "changefreq": "daily"},
            {"loc": "/search", "priority": 0.9, "changefreq": "daily"},
            {"loc": "/recruit", "priority": 0.8, "changefreq": "daily"},
            {"loc": "/alumni", "priority": 0.8, "changefreq": "weekly"},
            {"loc": "/IC/intro", "priority": 0.7, "changefreq": "monthly"},
            {"loc": "/IC/structure", "priority": 0.7, "changefreq": "monthly"},
            {"loc": "/IC/joinUs", "priority": 0.8, "changefreq": "monthly"},
            {"loc": "/IC/contactUs", "priority": 0.7, "changefreq": "monthly"},
            {"loc": "/smart-business-department", "priority": 0.95, "changefreq": "monthly"},
            {"loc": "/ic-department", "priority": 0.95, "changefreq": "monthly"},
            {"loc": "/nkust-ic", "priority": 0.95, "changefreq": "monthly"},
            {"loc": "/about-department", "priority": 0.9, "changefreq": "monthly"},
            {"loc": "/career-prospects", "priority": 0.9, "changefreq": "monthly"},
        ]

        for page in static_pages:
            urls.append({
                "loc": f"{base_url}{page['loc']}",
                "lastmod": timezone.now().strftime("%Y-%m-%d"),
                "priority": page["priority"],
                "changefreq": page["changefreq"]
            })

        # 動態公司頁面 - 暫時移除個別公司頁面
        # companies = Company.objects.filter(
        #     member__is_show=True,
        #     member__private__is_active=True
        # ).select_related('member')

        # for company in companies:
        #     if company.name:
        #         slug = slugify(company.name) if company.name else str(company.id)
        #         urls.append({
        #             "loc": f"{base_url}/company/{company.id}/{slug}",
        #             "lastmod": company.created_at.strftime("%Y-%m-%d") if company.created_at else timezone.now().strftime("%Y-%m-%d"),
        #             "priority": 0.7,
        #             "changefreq": "weekly"
        #         })

        # 招募資訊頁面
        recruits = Recruit.objects.filter(active=True)
        for recruit in recruits:
            if recruit.title:
                slug = slugify(recruit.title) if recruit.title else str(recruit.id)
                urls.append({
                    "loc": f"{base_url}/recruit/{recruit.id}/{slug}",
                    "lastmod": recruit.release_date.strftime("%Y-%m-%d") if recruit.release_date else timezone.now().strftime("%Y-%m-%d"),
                    "priority": 0.6,
                    "changefreq": "weekly"
                })

        # 文章頁面
        articles = Article.objects.filter(active=True)
        for article in articles:
            if article.title:
                slug = slugify(article.title) if article.title else str(article.id)
                urls.append({
                    "loc": f"{base_url}/article/{article.id}/{slug}",
                    "lastmod": article.created_at.strftime("%Y-%m-%d") if article.created_at else timezone.now().strftime("%Y-%m-%d"),
                    "priority": 0.6,
                    "changefreq": "monthly"
                })

        # 生成 XML 格式
        xml_content = self.generate_xml(urls)

        return Response(
            xml_content,
            content_type="application/xml"
        )

    def generate_xml(self, urls):
        """生成 XML 格式的 sitemap"""
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

        for url in urls:
            xml += '  <url>\n'
            xml += f'    <loc>{url["loc"]}</loc>\n'
            xml += f'    <lastmod>{url["lastmod"]}</lastmod>\n'
            xml += f'    <changefreq>{url["changefreq"]}</changefreq>\n'
            xml += f'    <priority>{url["priority"]}</priority>\n'
            xml += '  </url>\n'

        xml += '</urlset>'
        return xml


# 移除公司詳情 SEO View - 依照需求不需要個別公司頁面
# class CompanySEOView(APIView):
#     已移除...


class SearchSEOView(APIView):
    """搜尋頁面的 SEO 增強"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        search_query = request.GET.get('q', '')
        industry_id = request.GET.get('industry', None)

        meta_tags = {
            "title": f"搜尋 {search_query} - 智慧商務系系友企業" if search_query else "系友企業搜尋 - 國立高雄科技大學智慧商務系",
            "description": f"搜尋國立高雄科技大學智慧商務系系友企業，關鍵字：{search_query}" if search_query else "搜尋國立高雄科技大學智慧商務系系友企業，包含各產業領域的傑出企業",
            "canonical_url": f"https://nkusticalumni.org/search?q={search_query}" if search_query else "https://nkusticalumni.org/search"
        }

        # 熱門搜尋推薦
        hot_searches = [
            "人工智慧", "大數據", "電子商務",
            "數位行銷", "軟體開發", "金融科技"
        ]

        # 產業分類
        from apps.company.models import Industry
        industries = Industry.objects.all().values('id', 'title')

        return Response({
            "meta": meta_tags,
            "hot_searches": hot_searches,
            "industries": list(industries)
        })


class RobotsTxtView(APIView):
    """動態生成 robots.txt"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        content = """# robots.txt for https://nkusticalumni.org/
User-agent: *
Allow: /
Disallow: /manager/
Disallow: /admin/
Disallow: /api/token/
Disallow: /private/

# Allow search engines to access API endpoints for SEO
Allow: /api/seo/
Allow: /api/sitemap.xml
Allow: /api/company/search

# Crawl-delay for respectful crawling
Crawl-delay: 1

# Major search engines
User-agent: Googlebot
Allow: /
Crawl-delay: 0

User-agent: Bingbot
Allow: /
Crawl-delay: 1

# Sitemap
Sitemap: https://nkusticalumni.org/api/sitemap.xml
"""
        return Response(content, content_type="text/plain")