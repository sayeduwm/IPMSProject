"""geodjango URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url,patterns

from . import views
from . import tms

urlpatterns =[
    url(r'^$',views.listShapefiles,name='listShapefiles'),
    url(r'^import/$',views.importShapefile,name='importShapefile'),
    url(r'^import/import$',views.importShapefile,name='importShapefile'),
    url(r'^export/(?P<shapefile_id>\d+)$',views.exportShapefile,name= 'exportShapefile'),
    url(r'^delete/(?P<shapefile_id>\d+)$',views.deleteShapefile, name='deleteShapefile'),
    url(r'^tms/$',tms.root,name='root'),
    url(r'^tms/(?P<version>[0-9.]+)$',tms.service,name='service'),
    url(r'^tms/(?P<version>[0-9.]+)/' +  r'(?P<shapefile_id>\d+)$',tms.tileMap,name='tileMap'),
    url(r'^tms/(?P<version>[0-9.]+)/' +   r'(?P<shapefile_id>\d+)/(?P<zoom>\d+)/' +  r'(?P<x>\d+)/(?P<y>\d+)\.png$',tms.tile, name='tile'),
    url(r'^edit/(?P<shapefile_id>\d+)$',views.editShapefile,name='editShapefile'), # feature_id = None -> add.
    #url(r'^delete_feature/(?P<shapefile_id>\d+)/' +r'(?P<feature_id>\d+)$',views. delete_feature,          'delete_feature'),
    url(r'^findFeature/$',views.findFeature,name='findFeature'),
    url(r'^editFeature/(?P<shapefile_id>\d+)/' +  r'(?P<feature_id>\d+)$',views.editFeature,name='editFeature'),
    url(r'^geo/$',views.geolocation,name='geolocation'),
    url(r'^st/$',views.ins,name='ins'),
    url(r'^ipmsuna/$',views.ipmsindex,name='ipmsindex'),
    url(r'^ipmsuna/t/$',views.ins,name='ins'),
    url(r'^ipmsuna/u/$',views.studentinstant,name='studentinstant'),
    url(r'^ipmsuna/v/$',views.unastaff,name='unastaff'),
    url(r'^ipmsuna/x/$',views.checkreserve,name='checkreserve'),
    url(r'^ipmsuna/y/$',views.leavespot,name='leavespot'),
    
    
    ]



             


            
             
             
