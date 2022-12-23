from django.urls import path, include
from .views import home_page, PostCreate, post_page, PostEdit, delete_comment, accept_comment
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', home_page, name='home_page'),
    path('create/', PostCreate.as_view(), name='post_create'),
    path('filtred/<category>/', home_page, name='home_page_filtred'),
    path('<post>/', post_page, name='post_detail'),
    path('edit/<slug:slug>/', PostEdit.as_view(), name='post_edit'),
    path('<comment_id>/delete/', delete_comment, name='delete_comment'),
    path('<comment_id>/accept/', accept_comment, name='accept_comment'),
]



if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)