from rest_framework import serializers
from .models import User, VIA_EMAIL, VIA_PHONE, NEW
from shared.utility import email_or_phone_number


class SignupSerializer(serializers.ModelSerializer):
    email_phone_number = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email_phone_number',
            'auth_type_choices',
            'auth_status',
        )
        read_only_fields = ('id', 'auth_type_choices', 'auth_status')

    def validate(self, attrs):
        user_input = attrs.get('email_phone_number').lower()
        input_type = email_or_phone_number(user_input)
        print(input_type)

        if input_type == VIA_EMAIL:
            if User.objects.filter(email=user_input).exists():
                raise serializers.ValidationError("Email already registered")
            attrs['Email'] = user_input
            attrs['auth_type_choices'] = VIA_EMAIL

        elif input_type == VIA_PHONE:
            if User.objects.filter(phone_number=user_input).exists():
                raise serializers.ValidationError("Phone number already registered")
            attrs['Phone_number'] = user_input
            attrs['auth_type_choices'] = VIA_PHONE

        else:
            raise serializers.ValidationError("Invalid email or phone number")

        attrs['auth_status'] = NEW
        return attrs

    def create(self, validated_data):
        validated_data.pop('email_phone_number')

        user = User.objects.create(**validated_data)
        user.create_verify_code(user.auth_type_choices)
        return user




