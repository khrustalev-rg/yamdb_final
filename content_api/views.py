import uuid
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.mixins import DestroyModelMixin
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from content_api.filters import TitleFilter
from content_api.models import Category, Comment, Genre, Review, Title
from content_api.permissions import (IsAdmin, IsAdminOrReadOnly,
                                     IsStaffOrAuthorOrReadOnly)
from content_api.serializers import (CategorySerializer, CommentSerializer,
                                     GenreSerializer, ReveiwSerializer,
                                     TokenObtainPairSerializer,
                                     UserCodeSerializer, UserSerializer,
                                     TitleWriteSerializer, TitleListSerializer)
from users.models import User, UserCode

EMAIL = 'post@yamdb.com'


class UserCodeViewSet(CreateAPIView):
    serializer_class = UserCodeSerializer
    queryset = UserCode.objects.all()

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        email = self.request.data['email']
        code = uuid.uuid4()
        self.send_code(email, code)
        serializer.save(email=email, confirmation_code=code)

    @staticmethod
    def send_code(email, code):
        send_mail(
            f'Код доступа для регистрации на ресурсе YaMDB',
            f'{code}',
            EMAIL,
            [f'{email}'],
            fail_silently=False,
        )


class UserTokenViewSet(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        email = request.data.get('email')
        confirmation_code = request.data.get('confirmation_code')
        if not email:
            return Response("Email is required field.",
                            status=status.HTTP_400_BAD_REQUEST)
        if not confirmation_code:
            return Response("Confirmation code is required field.",
                            status=status.HTTP_400_BAD_REQUEST)
        if not UserCode.objects.filter(email=email,
                                       confirmation_code=confirmation_code):
            return Response("Confirmation code for your email isn't valid.",
                            status=status.HTTP_400_BAD_REQUEST)

        if not User.objects.filter(email=email):
            User.objects.create(email=email)
        serializer.is_valid(raise_exception=True)
        UserCode.objects.get(email=email).delete()
        return Response(serializer.validated_data,
                        status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, IsAdmin,)
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username', )

    @action(methods=('patch', 'get'), detail=False,
            permission_classes=(permissions.IsAuthenticated,),
            url_path='me', url_name='me')
    def me(self, request, *args, **kwargs):
        instance = self.request.user
        serializer = self.get_serializer(instance)
        if self.request.method == 'PATCH':
            serializer = self.get_serializer(
                instance, data=request.data, partial=True)
            serializer.is_valid()
            serializer.save()
        return Response(serializer.data)


class GenreCategoryViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                           DestroyModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name']
    lookup_field = 'slug'
    lookup_value_regex = '[^/]+'


class GenreViewSet(GenreCategoryViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(GenreCategoryViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    filter_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return TitleListSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReveiwSerializer
    permission_classes = (IsStaffOrAuthorOrReadOnly, )

    def get_queryset(self):
        queryset = Review.objects.filter(title=self.get_title()).all()
        return queryset

    def get_title(self):
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        return title

    def perform_create(self, serializer):
        queryset = self.get_queryset().filter(author=self.request.user)
        if queryset.exists():
            raise ValidationError({'detail': 'Такой обзор уже существует'})
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsStaffOrAuthorOrReadOnly,)

    def get_queryset(self):
        comments = Comment.objects.filter(review=self.get_review())
        return comments

    def get_review(self):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        return review

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
