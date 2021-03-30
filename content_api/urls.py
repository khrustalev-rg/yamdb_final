from django.urls import include, path
from rest_framework.routers import DefaultRouter

from content_api.views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                               ReviewViewSet, TitleViewSet, UserCodeViewSet,
                               UserTokenViewSet, UserViewSet)

router = DefaultRouter()
router.register('genres', GenreViewSet)
router.register('categories', CategoryViewSet)
router.register('titles', TitleViewSet)
router.register(r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet,
                basename='reviews')
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments')
router.register('users', UserViewSet)

auth_urlpatterns = [
    path('email/', UserCodeViewSet.as_view()),
    path('token/', UserTokenViewSet.as_view()),
]

urlpatterns = [
    path('v1/auth/', include(auth_urlpatterns)),
    path('v1/', include(router.urls)),
]
