import datetime as dt
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Avg
from content_api.models import Category, Comment, Genre, Review, Title
from users.models import User, UserCode


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('first_name', 'last_name', 'username', 'bio', 'role',
                  'email')
        model = User


class UserCodeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('email',)
        model = UserCode


class TokenObtainPairSerializer(serializers.Serializer):

    def validate(self, data):
        email = self.context['request'].data.get('email')
        if dt.datetime.now(dt.timezone.utc) - UserCode.objects.get(
                email=email).created >= dt.timedelta(minutes=720):
            raise serializers.ValidationError(
                f"Your verification code is outdated.")
        new_user = User.objects.get(email=email)
        refresh = self.get_token(new_user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        return data

    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)


class GenreSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(
        max_length=30,
        validators=[UniqueValidator(queryset=Genre.objects.all())]
    )

    class Meta:
        fields = ['name', 'slug']
        model = Genre


class CategorySerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(
        max_length=30,
        validators=[UniqueValidator(queryset=Category.objects.all())]
    )

    class Meta:
        fields = ['name', 'slug']
        model = Category


class TitleListSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    genre = GenreSerializer(many=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        fields = ['id', 'name', 'year', 'rating',
                  'description', 'genre', 'category']
        model = Title

    def get_rating(self, obj):
        rating = obj.reviews.all().aggregate(Avg('score'))
        return rating['score__avg']


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug', many=True)
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug')

    class Meta:
        fields = ['id', 'name', 'year', 'description', 'genre', 'category']
        model = Title


class ReveiwSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True, many=False,
    )

    class Meta:
        fields = ['id', 'text', 'author', 'score', 'pub_date']
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = ['id', 'text', 'author', 'pub_date']
        model = Comment
