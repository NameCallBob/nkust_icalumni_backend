from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from apps.company.models import Company
from apps.product.models import Product
from apps.picture.models import PromotionAd, ContinuousAd, OtherImage
from apps.picture.serializer import PromotionAdSerializer, ContinuousAdSerializer, OtherImageSerializer

class PromotionAdViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = PromotionAd.objects.all()
        serializer = PromotionAdSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = PromotionAdSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request):
        try:
            promotion_ad = PromotionAd.objects.get()
            serializer = PromotionAdSerializer(promotion_ad)
            return Response(serializer.data)
        except PromotionAd.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request):
        try:
            promotion_ad = PromotionAd.objects.get()
            promotion_ad.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except PromotionAd.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class ContinuousAdViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = ContinuousAd.objects.all()
        serializer = ContinuousAdSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = ContinuousAdSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, ):
        try:
            continuous_ad = ContinuousAd.objects.get()
            serializer = ContinuousAdSerializer(continuous_ad)
            return Response(serializer.data)
        except ContinuousAd.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, ):
        try:
            continuous_ad = ContinuousAd.objects.get()
            continuous_ad.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ContinuousAd.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class OtherImageViewSet(viewsets.ViewSet):

    def list(self, request):
        queryset = OtherImage.objects.all()
        serializer = OtherImageSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        company = request.user
        serializer = OtherImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request):
        try:
            other_image = OtherImage.objects.get("id",0)
            serializer = OtherImageSerializer(other_image)
            return Response(serializer.data)
        except OtherImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request):
        try:
            id=request.query_params.get("id",0)
            other_image = OtherImage.objects.get(id=id)
            other_image.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except OtherImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
