from rest_framework import serializers
from .models import User,UserProfile,Post,Comment
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed





class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        try:
            data = super().validate(attrs) 
        except AuthenticationFailed:
            if not User.objects.filter(username=attrs['username']).exists():
                raise AuthenticationFailed("Incorrect username or password")
            else:
                raise AuthenticationFailed("Incorrect username or password ")
        return data




# user serializer
class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="This email address is already registered. Please use another email.")]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    class Meta:
        model = User
        fields = ('id','username','email','password')
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }


    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        return user
    
    def validate_password(self, value):
        validate_password(value)
        return value
    
#  userprofile serializer

class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    date_joined = serializers.DateTimeField(source='user.date_joined', read_only=True)

    class Meta:
        model = UserProfile
        fields = ('id','first_name', 'last_name', 'gender', 'city','phone_number', 'country','street_address', 'birthday', 'bio', 'profile_picture','email','date_joined','facebook_url','instagram_url')


# posts
class PostSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    author_pics = serializers.SerializerMethodField() 
    tags = serializers.ListField(child=serializers.CharField(), write_only=True)

    class Meta:
        
        model = Post
        fields = ('id','author','title','content','post_image','slug','created_at','tags','author_pics')
        read_only_fields = ['id', 'created_at', 'slug', 'author']

    def get_author_pics(self, obj):
        return obj.author.userprofile.profile_picture.url if obj.author.userprofile.profile_picture else None

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])  
        post = Post.objects.create(**validated_data) 

        # Save tags to the post
        if tags:
            post.tags.set(tags) 
        
        return post
    
   
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['tags'] = [tag.name for tag in instance.tags.all()]  
        return representation
    
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        
        
        instance = super().update(instance, validated_data)
   
        if tags is not None:
            instance.tags.set(tags)
        
        instance.save()
        return instance



# comment

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    author_id = serializers.IntegerField(source='author.id',read_only=True)
    class Meta:
        model = Comment
        fields = ('id','author','text','created_at','author_id')
        read_only_fields = ['id', 'created_at', 'author']