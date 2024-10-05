from rest_framework import viewsets, status , permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.member.models import Member
from apps.company.models import Company , Industry
from apps.company.serializer import CompanySerializer ,IndustrySerializer

class CompanyViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Company.objects.all()
        serializer = CompanySerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        request.data['private'] = request.user.id
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request):
        try:
            company = Company.objects.get(
                member=Member.objects.get(
                private=request.user))
        except Company.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CompanySerializer(company)
        return Response(serializer.data)

    def update(self, request):
        try:
            company = Company.objects.get(
                member=Member.objects.get(
                    private=request.user))
        except Company.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CompanySerializer(company, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request):
        try:
            company = Company.objects.get(
                member=Member.objects.get(
                    private=request.user))
        except Company.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        company.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


from django.db.models import Q
from rest_framework import generics
from apps.company.models import Company
from apps.company.serializer import CompanySerializer

class CompanyListView(generics.ListAPIView):
    serializer_class = CompanySerializer
    authentication_classes=[]
    permission_classes=[permissions.AllowAny]

    def get_queryset(self):
        queryset = Company.objects.all()
        name = self.request.query_params.get('name', None)
        member = self.request.query_params.get('member', None)
        positions = self.request.query_params.get('positions', None)
        products = self.request.query_params.get('products', None)
        address = self.request.query_params.get('address', None)
        email = self.request.query_params.get('email', None)
        phone_number = self.request.query_params.get('phone_number', None)

        query = Q()
        if name:
            query &= Q(name__icontains=name)
        if member:
            query &= Q(member=member)
        if positions:
            query &= Q(positions__icontains=positions)
        if products:
            query &= Q(products__icontains=products)
        if address:
            query &= Q(address__icontains=address)
        if email:
            query &= Q(email__icontains=email)
        if phone_number:
            query &= Q(phone_number__icontains=phone_number)

        return queryset.filter(query)


class IndustryViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Industry.objects.all()
        serializer = IndustrySerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = IndustrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request):
        try:
            if request.data.get("id",'') == '':
                return Response(status=400,data="無參數")
            industry = Industry.objects.get(id=request.data.get('id'))
        except Industry.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = IndustrySerializer(industry)
        return Response(serializer.data)

    def update(self, request):
        try:
            if request.data.get("id",'') == '':
                return Response(status=400,data="無參數")
            industry = Industry.objects.get(id=request.data.get('id'))
        except Industry.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = IndustrySerializer(industry, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request):
        try:
            if request.data.get("id",'') == '':
                return Response(status=400,data="無參數")
            industry = Industry.objects.get(id=request.data.get('id'))
        except Industry.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        industry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)