from rest_framework import serializers
from .models import *
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, max_length=15, min_length=8)
    password_confirm = serializers.CharField(write_only=True, max_length=15, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']

    def save(self):
        user = User(
            username=self.validated_data['username'],
            email=self.validated_data['email'])
        password = self.validated_data['password']
        password_confirm = self.validated_data['password_confirm']

        if not user.username.isalnum():
            raise serializers.ValidationError("Username must consist of letters and numbers only.")

        if password != password_confirm:
            raise serializers.ValidationError("Passwords do not match.")
        user.set_password(password)
        user.save()


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=15, min_length=8, write_only=True)
    tokens = serializers.SerializerMethodField

    class Meta:
        model = User
        fields = ['username', 'password', 'tokens']

    def validate(self, attrs):
        username = attrs.get('username', '')
        password = attrs.get('password', '')

        user = auth.authenticate(username=username, password=password)
        if not user:
            raise AuthenticationFailed('Invalid credential, try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')

        return {
            'username': user.username,
            'tokens': user.tokens()
        }
