
from django.urls import path
from . import views

# Namespace for reversing in templates (templates use 'dashboard:...')
app_name = 'dashboard'

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
    path('payments/add/', views.add_payment_method, name='add_payment_method'),
    path('payments/<int:pk>/', views.payment_method_detail, name='payment_method_detail'),
    path('payments/<int:pk>/edit/', views.edit_payment_method, name='edit_payment_method'),
    path('payments/<int:pk>/delete/', views.delete_payment_method, name='delete_payment_method'),
    
    # Payment Verification URLs
    path('payment-verifications/', views.payment_verification_list, name='payment_verification_list'),
    path('payment-verifications/add/', views.add_payment_verification, name='add_payment_verification'),
    path('payment-verifications/my/', views.my_payment_verifications, name='my_payment_verifications'),
    path('payment-verifications/<int:pk>/', views.payment_verification_detail, name='payment_verification_detail'),
    path('payment-verifications/<int:pk>/verify/', views.verify_payment, name='verify_payment'),
    path('payment-verifications/<int:pk>/delete/', views.delete_payment_verification, name='delete_payment_verification'),
    
    path('class/<slug:level_slug>/', views.class_level_view, name='class_level'),



    # authentication paths
    path('login/', views.login_view, name='login'),
    # path('signup/', views.sign_up, name='signup'),
    path('logout/', views.logout_view, name='logout'),





# for CRUD operations of models
    # path('users/', views.user_list, name='user_list'),
    # path('users/add/', views.user_create, name='user_create'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    
    # Academic Level URLs
    # path('levels/', views.level_list, name='level_list'),
    # path('levels/add/', views.level_create, name='level_create'),
    path('levels/<int:pk>/', views.level_detail, name='level_detail'),
    path('levels/<int:pk>/delete/', views.level_delete, name='level_delete'),
    
    # Stream URLs
    # path('streams/', views.stream_list, name='stream_list'),
    # path('streams/add/', views.stream_create, name='stream_create'),
    path('streams/<int:pk>/', views.stream_detail, name='stream_detail'),
    path('streams/<int:pk>/delete/', views.stream_delete, name='stream_delete'),
    
    # Subject URLs
    # path('subjects/', views.subject_list, name='subject_list'),
    # path('subjects/add/', views.subject_create, name='subject_create'),
    path('subjects/<int:pk>/', views.subject_detail, name='subject_detail'),
    path('subjects/<int:pk>/delete/', views.subject_delete, name='subject_delete'),
    
    # Enrollment URLs
    # path('enrollments/', views.enrollment_list, name='enrollment_list'),
    # path('enrollments/add/', views.enrollment_create, name='enrollment_create'),
    path('enrollments/<int:pk>/', views.enrollment_detail, name='enrollment_detail'),
    path('enrollments/<int:pk>/delete/', views.enrollment_delete, name='enrollment_delete'),
    
    # Live Class URLs
    # path('live-classes/', views.liveclass_list, name='liveclass_list'),
    # path('live-classes/add/', views.liveclass_create, name='liveclass_create'),
    path('live-classes/<int:pk>/', views.liveclass_detail, name='liveclass_detail'),
    path('live-classes/<int:pk>/delete/', views.liveclass_delete, name='liveclass_delete'),
    
    # Extra Curricular Activity URLs
    # path('activities/', views.activity_list, name='activity_list'),
    # path('activities/add/', views.activity_create, name='activity_create'),
    path('activities/<int:pk>/', views.activity_detail, name='activity_detail'),
    path('activities/<int:pk>/delete/', views.activity_delete, name='activity_delete'),
    
    # Video URLs
    # path('videos/', views.video_list, name='video_list'),
    # path('videos/add/', views.video_create, name='video_create'),
    path('videos/<int:pk>/', views.video_detail, name='video_detail'),
    path('videos/<int:pk>/delete/', views.video_delete, name='video_delete'),
]

