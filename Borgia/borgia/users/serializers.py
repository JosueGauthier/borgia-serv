from django.contrib.auth import authenticate
from rest_framework import serializers

from django.contrib.auth.models import Group,Permission


from .models import User


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'last_name', 'first_name', 'password', 'email',
                  'surname', 'family', 'balance', 'year', 'campus', 'phone', 'avatar', 'theme')


class LoginSerializer(serializers.Serializer):
    """
    This serializer defines two fields for authentication:
      * username
      * password.
    It will try to authenticate the user with when validated.
    """
    username = serializers.CharField(
        label="Username",
        write_only=True
    )
    password = serializers.CharField(
        label="Password",
        # This will be used when the DRF browsable API is enabled
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    def validate(self, attrs):
        # Take username and password from request
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            # Try to authenticate the user using Django auth framework.
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)
            if not user:
                # If we don't have a regular user, raise a ValidationError
                msg = 'Access denied: wrong username or password.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Both "username" and "password" are required.'
            raise serializers.ValidationError(msg, code='authorization')
        # We have a valid user, put it in the serializer's validated_data.
        # It will be used in the view.
        attrs['user'] = user
        return attrs


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = [
            'id',
            'name',
            'permissions',
        ]
        depth = 1
        
class PermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Permission
        fields = [          
            'id',
            'name',
            'content_type',
            'codename'
        ]
        depth = 1

from django.contrib.auth.backends import ModelBackend



class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        #fields = '__all__'
        exclude = ('password','last_login',"is_superuser","is_staff","jwt_iat" )
        depth = 2