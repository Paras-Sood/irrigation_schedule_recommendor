from rest_framework.serializers import ModelSerializer
from backend.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

class UserSerializer(ModelSerializer):
    class Meta:
        model=User
        exclude = [
            "id",
            "is_active",
            "is_staff",
            "password",
            "is_superuser",
            "user_permissions",
            "groups",
            "last_login",
        ]
        read_only_fields = ["email",]

class RegisterSerializer(ModelSerializer):
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )

    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email')#, 'first_name', 'last_name')
        # extra_kwargs = {
        #     'first_name': {'required': True},
        # }

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            # first_name=validated_data['first_name'],
            # last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user