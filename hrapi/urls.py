from django.urls import path, include
from rest_framework import routers
from hrapi.views import EmployeeViewSet, IndustryViewSet, GeneralStatistic, YoEStats, AgeStats, GenderStats

router = routers.DefaultRouter()
router.register(r'employees', EmployeeViewSet)
router.register(r'industries', IndustryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('averages_per_industry/', GeneralStatistic.as_view(), name='averages_per_industry'),
    path('averages_per_yoe/', YoEStats.as_view(), name='averages_per_yoe'),
    path('agestats/', AgeStats.as_view(), name='agestats'),
    path('genderstats/', GenderStats.as_view(), name='genderstats'),
]
