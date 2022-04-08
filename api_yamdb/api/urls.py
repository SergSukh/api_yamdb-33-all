from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    SignUp,
    APIToken,
    UsersViewSet,    
    TitlesViewSet,
    GenresViewSet,
    CategoriesViewSet,
    AuthorViewSet,
    ReviewViewSet,
    CommentViewSet
)

router = DefaultRouter()

app_name = 'api'
router.register('auth/signup', SignUp, basename='signup')

router.register('users', UsersViewSet)
router.register('titles', TitlesViewSet)
router.register('genres', GenresViewSet, basename='genres')
router.register('categories', CategoriesViewSet, basename='categories')
router.register(
    r'titles/(?P<id>[\d]+)/reviews',
    ReviewViewSet,
    basename='reviews'
)

router.register(
    r'titles/(?P<title_id>[0-9]+)/reviews/'
    '(?P<review_id>[0-9]+)/comments',
    CommentViewSet,
    basename='comments'
)
router.register('author', AuthorViewSet)

urlpatterns = [
    path('v1/auth/token/', APIToken.as_view()),
    path('v1/', include(router.urls)),
]
