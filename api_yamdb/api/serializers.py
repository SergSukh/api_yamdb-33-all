import datetime as dt
from tkinter import CURRENT

from django.db.models import Avg
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from reviews.models import (Author, Categories, Comment, Genres, GenreTitle,
                            Review, Title)
from users.models import User


class SignUpSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(
        validators=[UniqueValidator(User.objects.all())],
        required=True
    )
    username = serializers.CharField(
        validators=[UniqueValidator(User.objects.all())],
        required=True
    )

    class Meta:
        model = User
        fields = ('username', 'email')


class TokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )


class MeSerializer(serializers.ModelSerializer):
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )


class AuthorSerializer(serializers.ModelSerializer):
    """
    Для отображения, поиска и фильтрации
    произведений по информации об
    автор (для расширения)."""

    titles = serializers.StringRelatedField(
        many=True,
        allow_null=True,
        read_only=True
    )

    class Meta:
        model = Author
        fields = ('slug', 'titles',)


class GenresSerializer(serializers.ModelSerializer):
    """Жанры, описание."""

    class Meta:
        model = Genres
        fields = ('name', 'slug')


class CategoriesSerializer(serializers.ModelSerializer):
    """Категории, описание."""

    class Meta:
        model = Categories
        fields = ('name', 'slug')


class TitlesSerializer(serializers.ModelSerializer):
    """Основной метод записи информации."""

    category = serializers.SlugRelatedField(
        slug_field='slug',
        many=False,
        queryset=Categories.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        required=False,
        queryset=Genres.objects.all()
    )
    author = serializers.SlugRelatedField(
        slug_field='slug',
        many=False,
        queryset=Author.objects.all(),
        required=False
    )
    reviews = serializers.StringRelatedField(
        many=True,
        read_only=True,
        allow_null=True
    )
    rating = serializers.SerializerMethodField()

    class Meta:
        fields = '__all__'
        model = Title
        validators = [
            UniqueTogetherValidator(
                queryset=Title.objects.all(),
                fields=('name', 'year', 'category')
            )
        ]

    def validate_year(self, value):
        current_year = dt.date.today().year
        if value > current_year:
            raise serializers.ValidationError('ПРоверьте год')
        return value

    def get_rating(self, obj):
        rating = obj.reviews.all().aggregate(score=Avg('score'))
        if rating['score']:
            return round(rating['score'], 2)
        return None

    def create(self, validated_data):
        """Определяем наличие жанров и прописываем."""
        if 'genre' not in self.initial_data:
            title = Title.objects.create(**validated_data)
            return title
        genres = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)
        for genre in genres:
           
            GenreTitle.objects.create(genre=genre, title=title)

        return title


class TitlesViewSerializer(serializers.ModelSerializer):
    """Основной метод получения информации."""

    category = CategoriesSerializer(many=False, required=True)
    genre = GenresSerializer(many=True, required=False)
    rating = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category'
        )
        model = Title
        validators = [
            UniqueTogetherValidator(
                queryset=Title.objects.all(),
                fields=('name', 'year', 'category')
            )
        ]

    def get_rating(self, obj):
        rating = obj.reviews.all().aggregate(score=Avg('score'))
        if rating['score']:
            return round(rating['score'], 2)
        return None


class ReviewsSerializer(serializers.ModelSerializer):
    """Ревью для произведений"""
    author = serializers.SlugRelatedField(
        slug_field='username',
        default=serializers.CurrentUserDefault(),
        read_only=True
    )
    title = serializers.PrimaryKeyRelatedField(
        many=False,
        default=CURRENT,
        queryset=Title.objects.all()
    )

    class Meta:
        fields = '__all__'
        model = Review
        lookup_field = 'slug'
        read_only_fields = ['title']
        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=('text', 'author', 'title')
            )
        ]

    def validate_score(self, value):
        if 0 >= value >= 10:
            raise serializers.ValidationError('Проверьте оценку')
        return value


class CommentsSerializer(serializers.ModelSerializer):
    """Комментарии на отзывы"""
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment

    def validate(self, data):
        if 'text' not in data.keys():
            result = dict.fromkeys(
                'text', 'This field is required!'
            )
            raise serializers.ValidationError(result)
        return data