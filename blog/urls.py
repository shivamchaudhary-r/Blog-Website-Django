from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.decorators import login_required

from posts.views import (
    index,
    post_list,
    post_detail,
    post_create,
    post_update,
    post_delete,
    IndexView,
    SearchView,
    PostListView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
)
from accounts import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('search/', SearchView.as_view(), name='search'),
    path('', IndexView.as_view(), name='home'),
    path('blog/', PostListView.as_view(), name='post-list'),
    path('create/', PostCreateView.as_view(), name='post-create'),
    path('post/<pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/<pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('accounts/register/', views.AuthorCreateView.as_view(), name='accounts_register'),
    path('accounts/profile/', login_required(views.AuthorUpdateView.as_view()), name='accounts_update',),
    path('tinymce/', include('tinymce.urls')),
    path('accounts/', include('allauth.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
