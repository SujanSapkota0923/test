from django.urls import path
from . import views


# Keep an application namespace to preserve reverse('dashboard:...') usage
app_name = 'dashboard'


# Dashboard routes (consolidated)
urlpatterns = [
    path('', views.dashboard_view, name='index'),
    path('search/', views.global_search_view, name='global_search'),
    path('courses/', views.course_home_view, name='course_home'),
    path('subjects/', views.subject_list_view, name='subject_home'),
    path('students/', views.student_list_view, name='student_home'),
    path('teachers/', views.teacher_list_view, name='teacher_home'),
    path('streams/', views.stream_list_view, name='stream_home'),
    path('enrollments/', views.enrollment_list_view, name='enrollment_home'),
    path('live/', views.live_classes_view, name='live_classes'),
    path('videos/', views.video_list_view, name='video_home'),
    path('payments/', views.payment_method_list, name='payment_method_list'),
    path('payment-verifications/', views.payment_verification_list, name='payment_verification_list'),
    path('class/<slug:level_slug>/', views.class_level_view, name='class_level'),

    # authentication paths
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # CRUD operations (detail/edit/delete)
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),

    path('levels/<int:pk>/', views.level_detail, name='level_detail'),
    path('levels/<int:pk>/delete/', views.level_delete, name='level_delete'),

    path('streams/<int:pk>/', views.stream_detail, name='stream_detail'),
    path('streams/<int:pk>/delete/', views.stream_delete, name='stream_delete'),

    path('subjects/<int:pk>/', views.subject_detail, name='subject_detail'),
    path('subjects/<int:pk>/delete/', views.subject_delete, name='subject_delete'),

    path('enrollments/<int:pk>/', views.enrollment_detail, name='enrollment_detail'),
    path('enrollments/<int:pk>/delete/', views.enrollment_delete, name='enrollment_delete'),

    path('live-classes/<int:pk>/', views.liveclass_detail, name='liveclass_detail'),
    path('live-classes/<int:pk>/delete/', views.liveclass_delete, name='liveclass_delete'),

    path('activities/<int:pk>/', views.activity_detail, name='activity_detail'),
    path('activities/<int:pk>/delete/', views.activity_delete, name='activity_delete'),

    path('videos/<int:pk>/', views.video_detail, name='video_detail'),
    path('videos/<int:pk>/delete/', views.video_delete, name='video_delete'),

    
    path('payments/<int:pk>/', views.payment_method_detail, name='payment_method_detail'),
    path('payments/<int:pk>/edit/', views.edit_payment_method, name='edit_payment_method'),
    path('payments/<int:pk>/delete/', views.delete_payment_method, name='delete_payment_method'),

    path('payment-verifications/my/', views.my_payment_verifications, name='my_payment_verifications'),
    path('payment-verifications/<int:pk>/', views.payment_verification_detail, name='payment_verification_detail'),
    path('payment-verifications/<int:pk>/verify/', views.verify_payment, name='verify_payment'),
    path('payment-verifications/<int:pk>/delete/', views.delete_payment_verification, name='delete_payment_verification'),




    # Add/create handlers (kept towards the bottom)
    path('users/add/', views.add_user, name='add_user'),
    path('academic-levels/add/', views.add_academic_level, name='add_academic_level'),
    path('streams/add/', views.add_stream, name='add_stream'),
    path('subjects/add/', views.add_subject, name='add_subject'),
    path('enrollments/add/', views.add_enrollment, name='add_enrollment'),
    path('live-classes/add/', views.add_live_class, name='add_live_class'),
    path('activities/add/', views.add_activity, name='add_activity'),
    path('videos/add/', views.add_video, name='add_video'),
    path('payments/add/', views.add_payment_method, name='add_payment_method'),
    path('payment-verifications/add/', views.add_payment_verification, name='add_payment_verification'),



    
    # List URLs (legacy names kept where templates expect them)
    path('subjects/list/', views.subject_list, name='subject_list'),
]