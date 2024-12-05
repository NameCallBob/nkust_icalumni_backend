from django.db import models
from django.db.models import Q
from apps.private.models import Private


class Position(models.Model):
    """
    系友會職位
    - title: 職位名稱，使用 TextField 儲存，例如「會長」、「副會長」等。
    - priority: 優先級，使用 IntegerField 儲存，用來表示職位的重要性或排序，數字越小表示優先級越高。
    """
    title = models.TextField()
    priority = models.IntegerField()

    def __str__(self):
        return self.title


class Graduate(models.Model):
    """
    畢業學校
    - school: 畢業的學校名稱，使用 TextField 儲存，例如「國立高雄科技大學」。
    - grade: 畢業年級，使用 CharField 儲存，例如「109級 or 112」。
    """
    school = models.TextField(default="國立高雄科技大學智慧商務系")
    grade = models.CharField(max_length=20, null=False)
    student_id = models.TextField(default="000000000")

    def __str__(self):
        return f"{self.school} - {self.grade}"


class Member(models.Model):
    """
    系友會會員
    - name: 會員的名字，使用 CharField 儲存。
    - home_phone: 市內電話號碼，使用 CharField 儲存，允許為空值。
    - mobile_phone: 行動電話號碼，使用 CharField 儲存，允許為空值。
    - gender: 性別，使用 CharField 儲存，選項包括 "M" (Male), "F" (Female), "O" (Other)。
    - address: 住址，使用 TextField 儲存，允許為空值。
    - is_paid: 是否繳費，使用 BooleanField 儲存，默認為 False。
    - intro: 自我介紹，使用 TextField 儲存，允許為空值。
    - birth_date: 生日，使用 DateField 儲存，允許為空值。
    - photo: 會員照片，使用 ImageField 儲存，上傳路徑設為 'static/'，允許為空值。
    - position: 會員的職位，使用 ForeignKey 連結到 Position 模型，如果職位被刪除，設為 NULL。
    - graduate: 會員的畢業學校，使用 ForeignKey 連結到 Graduate 模型，當學校資料被刪除時，會員資料也會被刪除。
    - date_joined: 加入日期，使用 DateField 儲存，默認為自動加入日期。
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    private = models.OneToOneField(Private, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    home_phone = models.CharField(max_length=15, blank=True, null=True)
    mobile_phone = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    address = models.TextField(blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    intro = models.TextField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    photo = models.ImageField(
        upload_to='static/member/', blank=True, null=True)
    position = models.ForeignKey(
        Position, on_delete=models.SET_NULL, null=True)
    graduate = models.OneToOneField(Graduate, on_delete=models.CASCADE, null=True)
    date_joined = models.DateField(auto_now_add=True)
    is_show = models.BooleanField("是否要展示於官網",default=False)

    def __str__(self):
        return f"{self.private} - {self.name} - {self.position}"

    @staticmethod
    def search_members(name=None, gender=None, school=None, position=None, is_paid=None, intro=None, search=None, is_active=None,is_show=None):
        """
        搜尋會員資料，可以根據名字、性別、學校、職位、是否繳費進行篩選，或根據 search 參數進行全域搜尋。

        :param name: 會員的名字 (部分或完整)
        :param gender: 會員的性別
        :param school: 畢業學校的名稱 (部分或完整)
        :param position: 職位名稱 (部分或完整)
        :param is_paid: 是否繳費
        :param intro: 自我介紹
        :param search: 搜尋所有欄位的關鍵字（排除照片）
        :return: 篩選後的會員 QuerySet
        """
        query = Q()

        if search:
            query &= (Q(name__icontains=search) |
                      Q(home_phone__icontains=search) |
                      Q(mobile_phone__icontains=search) |
                      Q(gender__icontains=search) |
                      Q(address__icontains=search) |
                      Q(intro__icontains=search) |
                      Q(position__title__icontains=search) |
                      Q(graduate__school__icontains=search))

        if name:
            query &= Q(name__icontains=name)
        if gender:
            query &= Q(gender=gender)
        if school:
            query &= Q(graduate__school__icontains=school)
        if position:
            query &= Q(position__title__icontains=position)
        if intro:
            query &= Q(intro__icontains=intro)
        if is_paid is not None:
            query &= Q(is_paid=is_paid)
        if is_active is not None:
            query &= Q(private__is_active=is_active)
        if is_show is not None:
            query &= Q(is_show=is_active)

        return Member.objects.filter(query)
