"""
URLs principales du projet UGANC
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Page d'accueil
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    
    # Modules
    path('auth/', include('apps.authentication.urls')),
    path('academique/', include('apps.gestion_academique.urls')),
    path('notes/', include('apps.gestion_notes.urls')),
    path('structure/', include('apps.structure_pedagogique.urls')),
    path('bulletins/', include('apps.bulletins.urls')),
]

# Servir les fichiers media en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Personnalisation de l'admin
admin.site.site_header = "UGANC - Administration"
admin.site.site_title = "UGANC Admin"
admin.site.index_title = "Gestion des Notes"
