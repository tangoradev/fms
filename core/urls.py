from django.urls import path
from .views_execution_course import execution_course_create

from .views import planification_course_manuelle

urlpatterns = [
    path('execution-course/create/<int:planification_id>/', execution_course_create, name='execution_course_create'),
    path('planification-course/manuelle/', planification_course_manuelle, name='planification_course_manuelle'),
    # ... autres patterns de l'app core ...
]
