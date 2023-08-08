from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import SimpleRouter

from store.views import BookViewSet, auth, UserBookRelationView

router = SimpleRouter()
router.register('book', BookViewSet)
router.register('book-relation', UserBookRelationView)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('social_django.urls', namespace='social')),
    path('auth/', auth),
    path("__debug__/", include("debug_toolbar.urls")),
]

urlpatterns += router.urls
