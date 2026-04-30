from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'confirm_password']
    
    def validated_email(self,value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError({"email":"Email already exists"})
        return value

    def validate(self, data):
        password = data.get("password")
        confirm_password = data.get("confirm_password")
        # password required 
        if not password or not confirm_password:
            raise serializers.ValidationError("Both password fields are required")
        # password matching condition 
        if password != confirm_password:
            raise serializers.ValidationError({
                "password": "Passwords do not match"
            })
        validate_password(password)
        return data
    # create user 
    def create(self, validated_data):
        validated_data.pop("confirm_password")
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class CustomTokenSerializer(TokenObtainPairSerializer):
    username_field="email"
