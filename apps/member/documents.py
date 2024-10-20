# documents.py  - 停用

from django_elasticsearch_dsl import Document, Index, fields
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import InnerDoc  # 正確導入 InnerDoc
from apps.member.models import Member,  Position, Graduate
from apps.company.models import Company, Industry
# 定義索引名稱
member_index = Index('members')
company_index = Index('companies')
position_index = Index('positions')
graduate_index = Index('graduates')
industry_index = Index('industries')

# 設定索引的設定（可選）
common_settings = {
    'number_of_shards': 1,
    'number_of_replicas': 0
}

member_index.settings(**common_settings)
company_index.settings(**common_settings)
position_index.settings(**common_settings)
graduate_index.settings(**common_settings)
industry_index.settings(**common_settings)

# 定義 Industry 的 Document
@registry.register_document
class IndustryDocument(Document):
    class Index:
        name = 'industries'

    class Django:
        model = Industry
        fields = [
            'title',
            'intro',
        ]

# 定義 Position 的 Document
@registry.register_document
class PositionDocument(Document):
    class Index:
        name = 'positions'

    class Django:
        model = Position
        fields = [
            'title',
            'priority',
        ]

# 定義 Graduate 的 Document
@registry.register_document
class GraduateDocument(Document):
    class Index:
        name = 'graduates'

    class Django:
        model = Graduate
        fields = [
            'school',
            'grade',
        ]

# 使用正確的 InnerDoc 定義嵌入式文件
class PositionInnerDoc(InnerDoc):
    title = fields.TextField()
    priority = fields.IntegerField()

class GraduateInnerDoc(InnerDoc):
    school = fields.TextField()
    grade = fields.TextField()

# 更新 MemberDocument，嵌入 Position 和 Graduate 的資料
@registry.register_document
class MemberDocument(Document):
    position = fields.ObjectField(doc_class=PositionInnerDoc)
    graduate = fields.ObjectField(doc_class=GraduateInnerDoc)

    class Index:
        name = 'members'

    class Django:
        model = Member
        fields = [
            'name',
            'home_phone',
            'mobile_phone',
            'gender',
            'address',
            'intro',
            'birth_date',
            'is_paid',
        ]

# 定義 Company 的 InnerDoc
class IndustryInnerDoc(InnerDoc):
    title = fields.TextField()
    intro = fields.TextField()

class MemberInnerDoc(InnerDoc):
    name = fields.TextField()
    mobile_phone = fields.TextField()

# 更新 CompanyDocument，嵌入 Industry 和 Member 的資料
@registry.register_document
class CompanyDocument(Document):
    industry = fields.ObjectField(doc_class=IndustryInnerDoc)
    member = fields.ObjectField(doc_class=MemberInnerDoc)

    class Index:
        name = 'companies'

    class Django:
        model = Company
        fields = [
            'name',
            'positions',
            'description',
            'products',
            'product_description',
            'website',
            'address',
            'email',
            'phone_number',
        ]
