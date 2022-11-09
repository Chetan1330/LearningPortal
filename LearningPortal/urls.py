"""LearningPortal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from qbank import views as qbank_view
from django.conf.urls.static import static 
from django.conf import settings
from django.urls import include
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse
from django.contrib.auth import views as auth_views


from qbank import models as models
from django.contrib.auth import views as auth_views


info_dict = {
    'queryset': models.ExamHeader.objects.all(),
    'date_field': 'date',
}


class StaticViewSitemap(Sitemap):
    def items(self):
        return ['home', 'catelogue', 'aboutus', 'contactus']
    def location(self, item):
        return reverse(item)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('import/', qbank_view.pdf_upload, name="import"),
    path('', qbank_view.home_view, name="home"),
    path('home/', qbank_view.home_view, name="home"),
    path('courses/', qbank_view.courses_view, name="courses"),
    #path('login/', qbank_view.login, name="login"),
    path('login/', auth_views.LoginView.as_view(next_page='home',redirect_authenticated_user=True,
     template_name='login.html', extra_context = {"courses": qbank_view.build_menu()}), name='login'),
    path('signup/', qbank_view.SignUpView.as_view(), name='signup'),
    path("logout/",auth_views.LogoutView.as_view(next_page='login'), name="logout"),
    path("aboutus/", auth_views.LogoutView.as_view(), name="aboutus"),
    path("contactus/", auth_views.LogoutView.as_view(), name="contactus"),
    path('exam_preview/<str:slug>', qbank_view.exampreview_view,name="exam_preview"),
     #Adding social auth path
    path('social-auth/', include('social_django.urls', namespace="social")),
    #path('exam_preview/', qbank_view.exampreview_view),
    path('exam/<str:slug>', qbank_view.exam_view, name="exam"),
    path('exam_question/<str:slug>/<int:question_num>', qbank_view.exam_question),
    path('reset_exam/<str:slug>', qbank_view.reset_exam),
    path('eval_exam/<str:slug>/<int:last_question>', qbank_view.evaluate_exam),
    path('summernote/', include('django_summernote.urls')),
     path('sitemap.xml', sitemap,
         {'sitemaps': {'course': GenericSitemap(info_dict, priority=0.6), 'static': StaticViewSitemap}},
         name='django.contrib.sitemaps.views.sitemap'),
    path('catalogue/', qbank_view.catalogue_view, name="catelogue"),
    path('certificate/<str:slug>', qbank_view.certificate_view),
    path('profile/', qbank_view.profile_view),
    path('dashboard/', qbank_view.dashboard_view, name="dashboard"),
    
]
urlpatterns+= static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
urlpatterns+= static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)