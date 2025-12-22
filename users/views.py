from rest_framework import permissions, status, generics
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import SignupSerializer
from .models import User


class CreateUserView(CreateAPIView):
    serializer_class = SignupSerializer
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)

class SignupApiview(APIView):
    serializer_class = SignupSerializer
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)

    def post(self,request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            'message': "Verification code sent successfully",
            'user_id': user.id
        },status=status.HTTP_201_CREATED)

class MockPurchaseView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self,request):
        user = request.user
        user.is_premium = True
        user.save(update_fields=['is_premium'])

        return Response({
            'detail': 'Premium activated'
        },
        status=status.HTTP_200_OK)



