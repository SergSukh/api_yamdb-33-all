import uuid

from rest_framework import status, viewsets, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.pagination import LimitOffsetPagination

from .permissions import (
    ReadOnlyOrOwnerOrAllAdmins, OwnerOrAdmins
)
from rest_framework import permissions
from rest_framework.decorators import action
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from .paginator import CommentPagination

from rest_framework.permissions import (
    IsAdminUser,
    AllowAny,
    IsAuthenticatedOrReadOnly
)
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail

from .permissions import (
    IsAdminOrReadOnly,
    ReadOnlyOrAdmins,
)
from .serializers import (
    SignUpSerializer,
    TokenSerializer,
    UsersSerializer
)

from composition.models import Titles, Genres, Categories, Author
from reviews.models import Reviews, User, Comment
from .serializers import (
    TitlesSerializer,
    TitlesViewSerializer,
    AuthorSerializer,
    CategoriesSerializer,
    GenresSerializer,
    ReviewsSerializer,
    CommentsSerializer
)


class SignUp(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_class = [AllowAny]

    # def get_queryset(self):
    #    user = get_object_or_404(User, username=self.request.user.username)
    #    queryset = User.objects.all().filter(username=user)
    #    print(1111111111, user, queryset)
    #    return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)

    def perform_create(self, serializer):
        confirmation_code = str(uuid.uuid4())
        # username = serializer.validated_data['username']
        email = serializer.validated_data['email']
        if email not in User.objects.all():
            serializer.save(confirmation_code=confirmation_code)
        return send_mail(
            'Код подверждения',
            confirmation_code,
            ['admin@email.com'],
            [email],
            fail_silently=False
        )


class APIToken(APIView):
    queryset = User.objects.all()
    serializer_class = TokenSerializer
    permission_class = [AllowAny]

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.data['username']
        confirmation_code = serializer.data['confirmation_code']
        user_base = get_object_or_404(User, username=username)
        if confirmation_code == user_base.confirmation_code:
            token = str(AccessToken.for_user(user_base))
            return Response({'token': token}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    pagination_class = CommentPagination
    permission_classes = (OwnerOrAdmins,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    @action(
        methods=[
            "get",
            "patch",
        ],
        detail=False,
        url_path="me",
        permission_classes=[permissions.IsAuthenticated]
    )
    def get_patch_user(self, request):
        user = get_object_or_404(User, username=self.request.user)
        if self.request.method == 'GET':
            serializers = self.get_serializer(user)
            return Response(serializers.data)
        if self.request.method == 'PATCH':
            serializers = self.get_serializer(
                user,
                data=request.data,
                partial=True
            )
            serializers.is_valid(raise_exception=True)
            serializers.save(role=user.role)
        return Response(serializers.data)


class UsernameViewSet(viewsets.ModelViewSet):
    serializer_class = UsersSerializer
    permission_classes = [AllowAny]
    permission_classes = [ReadOnlyOrAdmins]

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        print(self.kwargs.get('username'), user.email)
        queryset = User.objects.all().filter(username=user)
        return queryset


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Titles.objects.all()
    serializer_class = TitlesSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'year', 'genre', 'category', 'author')

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitlesViewSerializer
        return TitlesSerializer


class CategoriesViewSet(viewsets.ModelViewSet):
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    lookup_field = 'slug'
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAdminOrReadOnly
    ]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'slug')


class GenresViewSet(viewsets.ModelViewSet):
    queryset = Genres.objects.all()
    serializer_class = GenresSerializer
    lookup_field = 'slug'
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'slug')


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewsSerializer
    pagination_class = CommentPagination
    permission_classes = (ReadOnlyOrOwnerOrAllAdmins,)

    def get_queryset(self):
        # title_id = self.kwargs.get('id')
        title = get_object_or_404(Titles, id=self.kwargs.get('id'))
        #new_queryset = Reviews.objects.filter(
        #    title__pk=title_id
        #).order_by('-id')
        new_queryset = title.reviews.all()
        return new_queryset

    def perform_create(self, serializer):
        # title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Titles, id=self.kwargs.get('id'))
        if serializer.is_valid():
            if title.reviews.filter(author=self.request.user).exists():
                return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(author=self.request.user, title=title)
        raise ValidationError(
            'Reviews with this Title and Owner already exists.'
            )


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentsSerializer
    pagination_class = CommentPagination
    permission_classes = (ReadOnlyOrOwnerOrAllAdmins,)

    def get_queryset(self):
        # Получаем id title из эндпоинта
        review = get_object_or_404(Reviews, id = self.kwargs.get('review_id'))
        queryset = review.comments.all()
        return queryset

    def perform_create(self, serializer):
        review = get_object_or_404(Reviews, id = self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)

