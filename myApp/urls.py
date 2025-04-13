from django.urls import path

from myApp.views import download_image,VideoDownloadView,MovieDownloadView,contact,about



urlpatterns = [
    
    path('', download_image, name='download_image'),
    path('download_video/', VideoDownloadView.as_view(), name='download_video'),
    path('download_movie/', MovieDownloadView.as_view(), name='download_movie'),
    path('contact', contact, name='contact'),
    path('about/',about , name='about'),


    
]
