from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import UserProfile,User,Post,Comment
from .serializers import UserSerializer,UserProfileSerializer,PostSerializer,CommentSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer



# login
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# Create your views here.
class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save() 
        UserProfile.objects.create(user=user)

# update user profile
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    profile = get_object_or_404(UserProfile, user=user)
    if request.method == 'GET':
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
            
        if serializer.is_valid():
            serializer.save()
            user.has_profile = True
            user.save()
            return Response({
                "message": "Profile updated successfully!",
                "profile": serializer.data
            })
    
    return Response(serializer.errors, status=400)


# view profile
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_profile(request):
    user = request.user
    profile = get_object_or_404(UserProfile,user=user)
    serializer = UserProfileSerializer(profile)
    return Response(serializer.data)

# dashboad
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboad(request):
    user = request.user
    if not user.has_profile:
        create_profile_url = reverse('update_profile')
        return Response({'detail': 'Profile not found. Please complete your profile first.', 'redirect_url': create_profile_url}, status=403)

    try:
        profile = UserProfile.objects.get(user=user)
        profile_serializer = UserProfileSerializer(profile)
    
        posts = Post.objects.filter(author=user)
        posts_serializer = PostSerializer(posts, many=True)

        dashboard_data = {
        'profile': profile_serializer.data,
        'posts': posts_serializer.data
        }
        return Response(dashboard_data)

    except UserProfile.DoesNotExist:
        return Response({'detail': 'Profile not found.'}, status=404)

# create post  
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_post(request):
    if not request.user.has_profile:
            return Response(
                {"error": "You need to complete your profile before creating a post."},
                status=status.HTTP_403_FORBIDDEN
            )
    serializer = PostSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# get all post
@api_view(["GET"])
@permission_classes([AllowAny])
def posts_list(request):
    try:
        tag = request.query_params.get('tag', None) 
        if tag:
            posts = Post.objects.filter(tags__name__iexact=tag).order_by('-created_at') 
        else:
            posts = Post.objects.all().order_by('-created_at')
        
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Post.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

# get a particular post
@api_view(["GET"])
@permission_classes([AllowAny])
def post_detail(request,slug):
    post = get_object_or_404(Post,slug=slug)
    serializer = PostSerializer(post)
    return Response(serializer.data, status=status.HTTP_200_OK)


# edit post
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def edit_post(request,slug):
    post = get_object_or_404(Post, slug=slug)

    if request.user != post.author:
        return Response({"detail": "You do not have permission to edit this post."}, status=status.HTTP_403_FORBIDDEN)
    
     # full update
    if request.method == "PUT":
        serializer = PostSerializer(post,data=request.data)
         # Partial update
    elif request.method == 'PATCH': 
        serializer = PostSerializer(post, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# delete post
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def post_delete(request, slug):
    post = get_object_or_404(Post, slug=slug)

    if request.user != post.author:
        return Response({"detail": "You do not have permission to delete this post."}, status=status.HTTP_403_FORBIDDEN)

    post.delete()
    return Response({"detail": "Post deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


# create comment
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_comment(request, slug):
    post = get_object_or_404(Post, slug=slug)
    serializer = CommentSerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        serializer.save(post=post, author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# get all comment for a particular post
@api_view(["GET"])
@permission_classes([AllowAny])
def get_comment_for_post(request,slug):
    post = get_object_or_404(Post,slug=slug)

    comments = Comment.objects.filter(post=post)

    serializer = CommentSerializer(comments,many=True)
    return Response(serializer.data,status=status.HTTP_200_OK)



# delete comment
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def comment_delete(request, id):
    comment = get_object_or_404(Comment, id=id)

    if request.user != comment.author:
        return Response({"detail": "You do not have permission to delete this comment."}, status=status.HTTP_403_FORBIDDEN)

    comment.delete()
    return Response({"detail": "Comment deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


# check if user has profile
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def has_profile(request):
    user = request.user
    if not user.has_profile:
        return Response(
            {"error": "You need to complete your profile before creating a post."},
            status=status.HTTP_403_FORBIDDEN
        )
    return Response(
        {"message": "Profile is complete, you can create a post."},
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    user = request.user
    data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }
    return Response(data)


@api_view(['GET'])
@permission_classes([AllowAny])
def user_details(request, username):
    user = get_object_or_404(User, username=username)
    user_profile = get_object_or_404(UserProfile, user=user)
    serializer = UserProfileSerializer(user_profile)
    user_posts = Post.objects.filter(author=user)
    posts_serializer = PostSerializer(user_posts, many=True)
    return Response({
        'user_profile': serializer.data,
        'posts': posts_serializer.data
    })



