# Global Search Feature Documentation

## Overview

This document provides a comprehensive guide to implementing a powerful global search feature in Django applications. The search system supports:

- **Universal search** across all database models
- **Prefix-based filtering** for targeted searches (e.g., `user:john`, `course:physics`)
- **Real-time search** with keyboard shortcuts
- **Responsive UI** with modern design
- **Error handling** with graceful degradation

## Features

✨ **Multi-Model Search**: Search across Users, Students, Teachers, Courses, Subjects, Levels, Streams, Videos, Live Classes, and Enrollments in a single query

🎯 **Smart Filtering**: Use prefixes like `student:`, `course:`, `video:` to search specific categories

⌨️ **Keyboard Shortcuts**: Press `/` to focus search, `ESC` to clear

📱 **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices

🔍 **Real-time Results**: See results as you type with clear visual indicators

## Table of Contents

1. [Installation](#installation)
2. [Backend Setup](#backend-setup)
3. [Frontend Setup](#frontend-setup)
4. [Usage](#usage)
5. [Customization](#customization)
6. [Troubleshooting](#troubleshooting)

---

## Installation

### Prerequisites

- Django 3.2+
- Python 3.8+
- Bootstrap 5 (for UI styling)
- FontAwesome 5+ (for icons)

### Step 1: Install Required Packages

```bash
pip install django
```

No additional packages required! This feature uses Django's built-in ORM and Q objects.

---

## Backend Setup

### Step 1: Create the Search View

Add this view to your `views.py` (typically in `apps/Dashboard/views.py` or similar):

```python
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q
from apps.Course import models  # Import your models

@login_required
def global_search_view(request):
    """
    Global search view that searches across all models in the application.
    
    Supports prefix-based filtering:
    - user:john -> searches only users
    - student:jane -> searches only students
    - course:physics -> searches only courses
    - subject:math -> searches only subjects
    - level:grade -> searches only academic levels
    - stream:science -> searches only streams
    - video:tutorial -> searches only videos
    - live:quantum -> searches only live classes
    - enrollment:john -> searches only enrollments
    
    Without prefix, searches all categories.
    """
    query = request.GET.get('q', '').strip()
    
    # Initialize results dictionary with empty lists
    results = {
        'query': query,
        'users': [],
        'students': [],
        'teachers': [],
        'courses': [],
        'subjects': [],
        'levels': [],
        'streams': [],
        'videos': [],
        'live_classes': [],
        'enrollments': [],
        'error': None,
    }
    
    # Return empty results if no query
    if not query:
        return render(request, 'dashboard/search_results.html', results)
    
    # Parse search query for prefixes
    search_type = None
    search_term = query
    
    # Map prefixes to search types
    prefix_map = {
        'user': 'users',
        'users': 'users',
        'student': 'students',
        'students': 'students',
        'teacher': 'teachers',
        'teachers': 'teachers',
        'course': 'courses',
        'courses': 'courses',
        'subject': 'subjects',
        'subjects': 'subjects',
        'level': 'levels',
        'levels': 'levels',
        'class': 'levels',
        'classes': 'levels',
        'stream': 'streams',
        'streams': 'streams',
        'video': 'videos',
        'videos': 'videos',
        'live': 'live_classes',
        'enrollment': 'enrollments',
        'enrollments': 'enrollments',
    }
    
    # Check if query contains a colon (prefix indicator)
    if ':' in query:
        parts = query.split(':', 1)
        if len(parts) == 2:
            prefix = parts[0].lower().strip()
            term = parts[1].strip()
            
            # Only use prefix if it's valid and term is not empty
            if prefix in prefix_map and term:
                search_type = prefix_map[prefix]
                search_term = term
    
    # If no specific type, search all with original query
    if not search_type:
        search_term = query
    
    # If search_term is empty after parsing, use original query
    if not search_term:
        search_term = query
    
    # Determine if we should search all categories
    search_all = (search_type is None)
    
    try:
        # Search Users (only when specifically requested with "user:" prefix)
        if search_type == 'users':
            results['users'] = list(models.User.objects.filter(
                Q(username__icontains=search_term) |
                Q(first_name__icontains=search_term) |
                Q(last_name__icontains=search_term) |
                Q(email__icontains=search_term) |
                Q(phone__icontains=search_term)
            )[:20])
        
        # Search Students only
        if search_all or search_type == 'students':
            results['students'] = list(models.User.objects.filter(
                role=models.User.Role.STUDENT
            ).filter(
                Q(username__icontains=search_term) |
                Q(first_name__icontains=search_term) |
                Q(last_name__icontains=search_term) |
                Q(email__icontains=search_term) |
                Q(phone__icontains=search_term)
            )[:20])
        
        # Search Teachers only
        if search_all or search_type == 'teachers':
            results['teachers'] = list(models.User.objects.filter(
                role=models.User.Role.TEACHER
            ).filter(
                Q(username__icontains=search_term) |
                Q(first_name__icontains=search_term) |
                Q(last_name__icontains=search_term) |
                Q(email__icontains=search_term) |
                Q(phone__icontains=search_term)
            )[:20])
        
    # Search Courses (Course model)
        if search_all or search_type == 'courses':
      results['courses'] = list(models.Course.objects.filter(
                Q(title__icontains=search_term) |
                Q(description__icontains=search_term)
            )[:20])
        
        # Search Subjects
        if search_all or search_type == 'subjects':
            results['subjects'] = list(models.Subject.objects.filter(
                Q(name__icontains=search_term) |
                Q(description__icontains=search_term)
            )[:20])
        
        # Search Academic Levels
        if search_all or search_type == 'levels':
            results['levels'] = list(models.AcademicLevel.objects.filter(
                Q(name__icontains=search_term) |
                Q(slug__icontains=search_term)
            )[:20])
        
        # Search Streams
        if search_all or search_type == 'streams':
            results['streams'] = list(models.Stream.objects.filter(
                Q(name__icontains=search_term)
            )[:20])
        
        # Search Videos
        if search_all or search_type == 'videos':
            results['videos'] = list(models.Video.objects.filter(
                Q(title__icontains=search_term) |
                Q(description__icontains=search_term)
            )[:20])
        
        # Search Live Classes
        if search_all or search_type == 'live_classes':
            results['live_classes'] = list(models.LiveClass.objects.filter(
                Q(title__icontains=search_term) |
                Q(description__icontains=search_term)
            )[:20])
        
        # Search Enrollments
        if search_all or search_type == 'enrollments':
            results['enrollments'] = list(models.Enrollment.objects.filter(
                Q(student__username__icontains=search_term) |
                Q(student__first_name__icontains=search_term) |
                Q(student__last_name__icontains=search_term) |
                Q(level__name__icontains=search_term)
            )[:20])
    
    except Exception as e:
        # Log the error and show a friendly message
        results['error'] = f"An error occurred during search: {str(e)}"
        import traceback
        print(f"Search error: {str(e)}")
        print(traceback.format_exc())
    
    # Add search metadata to results
    results['search_type'] = search_type
    results['search_term'] = search_term
    
    return render(request, 'dashboard/search_results.html', results)
```

### Step 2: Add URL Pattern

Add this to your `urls.py` (typically in `apps/Dashboard/urls.py`):

```python
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # ... your other URL patterns ...
    path('search/', views.global_search_view, name='global_search'),
    # ... more URL patterns ...
]
```

### Step 3: Import Required Models

Make sure you have the following imports in your `views.py`:

```python
from django.db.models import Q, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
```

---

## Frontend Setup

### Step 1: Add Search Bar to Base Template

Add this search bar to your `base.html` or layout template (inside the header):

```html
<!-- Search Box -->
<div class="col d-flex justify-content-center justify-content-lg-end pe-lg-4">
  <div class="app-search-box-modern">
    <form class="app-search-form" action="{% url 'dashboard:global_search' %}" method="GET" role="search">
      <div class="search-wrapper">
        <i class="fas fa-search search-icon"></i>
        <input id="global-search" type="text" placeholder="Search anything... (try: user:john)" 
               name="q" aria-label="Search" class="search-input" 
               autocomplete="off" autocapitalize="off" spellcheck="false" />
        <button type="button" class="btn-clear-search" title="Clear" aria-label="Clear search" hidden>
          <i class="fas fa-times"></i>
        </button>
        <kbd class="search-shortcut">/</kbd>
      </div>
    </form>
  </div>
</div>
```

### Step 2: Add Search Bar Styles

Add this CSS to your main stylesheet or in a `<style>` block:

```css
/* Modern Search Bar Styles */
.app-search-box-modern {
  width: 100%;
  max-width: 450px;
}

.search-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  background: #f8f9fa;
  border: 2px solid transparent;
  border-radius: 24px;
  padding: 8px 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.search-wrapper:hover {
  background: #fff;
  border-color: rgba(21, 163, 98, 0.2);
  box-shadow: 0 4px 12px rgba(21, 163, 98, 0.08);
}

.search-wrapper:focus-within {
  background: #fff;
  border-color: #15a362;
  box-shadow: 0 4px 20px rgba(21, 163, 98, 0.15);
  transform: translateY(-1px);
}

.search-icon {
  color: #9ca3af;
  font-size: 16px;
  margin-right: 12px;
  transition: color 0.3s ease;
}

.search-wrapper:focus-within .search-icon {
  color: #15a362;
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  font-size: 15px;
  color: #1f2937;
  padding: 4px 0;
  font-weight: 400;
}

.search-input::placeholder {
  color: #9ca3af;
  font-weight: 400;
}

.btn-clear-search {
  background: none;
  border: none;
  color: #9ca3af;
  padding: 4px 8px;
  cursor: pointer;
  border-radius: 50%;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 4px;
}

.btn-clear-search:hover {
  background: rgba(21, 163, 98, 0.1);
  color: #15a362;
}

.btn-clear-search i {
  font-size: 14px;
}

.search-shortcut {
  background: #e5e7eb;
  color: #6b7280;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  margin-left: 8px;
  font-family: monospace;
  border: 1px solid #d1d5db;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
}

.search-wrapper:focus-within .search-shortcut {
  opacity: 0;
  transform: scale(0.9);
}

/* Responsive adjustments */
@media (max-width: 991px) {
  .app-search-box-modern {
    max-width: 100%;
  }
}

@media (max-width: 576px) {
  .search-wrapper {
    padding: 6px 12px;
  }
  
  .search-input {
    font-size: 14px;
  }
  
  .search-shortcut {
    display: none;
  }
}
```

### Step 3: Add Search Bar JavaScript

Add this JavaScript at the bottom of your base template (before `</body>`):

```html
<script>
  // Modern search bar enhancements
  document.addEventListener('DOMContentLoaded', function () {
    const input = document.getElementById('global-search');
    const clearBtn = document.querySelector('.btn-clear-search');
    const searchWrapper = document.querySelector('.search-wrapper');

    if (!input || !clearBtn) return;

    const updateState = () => {
      const hasValue = input.value && input.value.trim().length > 0;
      clearBtn.hidden = !hasValue;
    };

    input.addEventListener('input', updateState);
    
    clearBtn.addEventListener('click', () => {
      input.value = '';
      input.focus();
      updateState();
    });

    // Quick focus shortcut: press '/' to focus search
    window.addEventListener('keydown', (e) => {
      if (e.key === '/' && !e.ctrlKey && !e.metaKey && !e.altKey) {
        const tag = (document.activeElement && document.activeElement.tagName) || '';
        if (!['INPUT', 'TEXTAREA', 'SELECT'].includes(tag)) {
          e.preventDefault();
          input.focus();
        }
      }
      
      // ESC to clear and blur
      if (e.key === 'Escape' && document.activeElement === input) {
        input.value = '';
        input.blur();
        updateState();
      }
    });

    updateState();
  });
</script>
```

### Step 4: Create Search Results Template

Create a file `templates/dashboard/search_results.html`:

```html
{% extends 'dashboard/base.html' %}
{% load static %}

{% block title %}Search Results{% endblock %}

{% block content %}
<div class="app-wrapper">
  <div class="app-content pt-3 p-md-3 p-lg-4">
    <div class="container-xl">
      
      <div class="row g-3 mb-4 align-items-center justify-content-between">
        <div class="col-auto">
          <h1 class="app-page-title mb-0">Search Results</h1>
        </div>
      </div>
      
      {% if error %}
        <div class="alert alert-danger mb-4">
          <div class="d-flex align-items-center">
            <i class="fas fa-exclamation-triangle me-3"></i>
            <div>
              <strong>Error:</strong> {{ error }}
            </div>
          </div>
        </div>
      {% endif %}
      
      {% if query %}
        <div class="alert alert-info mb-4">
          <div class="d-flex align-items-center">
            <i class="fas fa-search me-3"></i>
            <div>
              <strong>Search Query:</strong> 
              {% if search_type %}
                <span class="badge bg-primary">{{ search_type }}</span>
              {% else %}
                <span class="badge bg-success">All Categories</span>
              {% endif %}
              "{{ search_term }}"
              <p class="mb-0 mt-2 small text-muted">
                <strong>Tip:</strong> Use prefixes like <code>user:</code>, <code>student:</code>, <code>teacher:</code>, <code>course:</code>, <code>subject:</code>, <code>level:</code>, <code>stream:</code>, <code>video:</code>, <code>live:</code>, or <code>enrollment:</code> to filter results.
              </p>
              <p class="mb-0 mt-2 small">
                <strong>Results found in:</strong>
                {% if users|length > 0 %}<span class="badge bg-secondary me-1">Users ({{ users|length }})</span>{% endif %}
                {% if students|length > 0 %}<span class="badge bg-success me-1">Students ({{ students|length }})</span>{% endif %}
                {% if teachers|length > 0 %}<span class="badge bg-info me-1">Teachers ({{ teachers|length }})</span>{% endif %}
                {% if courses|length > 0 %}<span class="badge bg-warning me-1">Courses ({{ courses|length }})</span>{% endif %}
                {% if subjects|length > 0 %}<span class="badge bg-primary me-1">Subjects ({{ subjects|length }})</span>{% endif %}
                {% if levels|length > 0 %}<span class="badge bg-secondary me-1">Levels ({{ levels|length }})</span>{% endif %}
                {% if streams|length > 0 %}<span class="badge bg-info me-1">Streams ({{ streams|length }})</span>{% endif %}
                {% if videos|length > 0 %}<span class="badge bg-danger me-1">Videos ({{ videos|length }})</span>{% endif %}
                {% if live_classes|length > 0 %}<span class="badge bg-success me-1">Live Classes ({{ live_classes|length }})</span>{% endif %}
                {% if enrollments|length > 0 %}<span class="badge bg-primary me-1">Enrollments ({{ enrollments|length }})</span>{% endif %}
              </p>
            </div>
          </div>
        </div>
        
        <!-- Students Results -->
        {% if students %}
        <div class="app-card app-card-orders-table shadow-sm mb-4">
          <div class="app-card-header p-3">
            <div class="row align-items-center">
              <div class="col">
                <h4 class="app-card-title mb-0">
                  <i class="fas fa-user-graduate text-success me-2"></i>
                  Students ({{ students|length }})
                </h4>
              </div>
            </div>
          </div>
          <div class="app-card-body">
            <div class="table-responsive">
              <table class="table table-hover mb-0">
                <thead>
                  <tr>
                    <th>Username</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Phone</th>
                    <th>Level</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {% for student in students %}
                  <tr>
                    <td>{{ student.username }}</td>
                    <td>{{ student.first_name }} {{ student.last_name }}</td>
                    <td>{{ student.email }}</td>
                    <td>{{ student.phone|default:"-" }}</td>
                    <td>{{ student.academic_level.name|default:"-" }}</td>
                    <td>
                      <a href="{% url 'dashboard:user_detail' student.pk %}" class="btn btn-sm btn-success">
                        <i class="fas fa-eye"></i> View
                      </a>
                    </td>
                  </tr>
                  {% endfor %}
                </tbody>
              </table>
            </div>
          </div>
        </div>
        {% endif %}
        
        <!-- Teachers Results -->
        {% if teachers %}
        <div class="app-card app-card-orders-table shadow-sm mb-4">
          <div class="app-card-header p-3">
            <div class="row align-items-center">
              <div class="col">
                <h4 class="app-card-title mb-0">
                  <i class="fas fa-chalkboard-teacher text-info me-2"></i>
                  Teachers ({{ teachers|length }})
                </h4>
              </div>
            </div>
          </div>
          <div class="app-card-body">
            <div class="table-responsive">
              <table class="table table-hover mb-0">
                <thead>
                  <tr>
                    <th>Username</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Phone</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {% for teacher in teachers %}
                  <tr>
                    <td>{{ teacher.username }}</td>
                    <td>{{ teacher.first_name }} {{ teacher.last_name }}</td>
                    <td>{{ teacher.email }}</td>
                    <td>{{ teacher.phone|default:"-" }}</td>
                    <td>
                      <a href="{% url 'dashboard:user_detail' teacher.pk %}" class="btn btn-sm btn-info">
                        <i class="fas fa-eye"></i> View
                      </a>
                    </td>
                  </tr>
                  {% endfor %}
                </tbody>
              </table>
            </div>
          </div>
        </div>
        {% endif %}
        
        <!-- Courses Results -->
        {% if courses %}
        <div class="app-card app-card-orders-table shadow-sm mb-4">
          <div class="app-card-header p-3">
            <div class="row align-items-center">
              <div class="col">
                <h4 class="app-card-title mb-0">
                  <i class="fas fa-graduation-cap text-warning me-2"></i>
                  Courses ({{ courses|length }})
                </h4>
              </div>
            </div>
          </div>
          <div class="app-card-body">
            <div class="table-responsive">
              <table class="table table-hover mb-0">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Description</th>
                    <th>Cost</th>
                    <th>Start Date</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {% for course in courses %}
                  <tr>
                    <td>{{ course.title }}</td>
                    <td>{{ course.description|truncatewords:10 }}</td>
                    <td>${{ course.cost }}</td>
                    <td>{{ course.start_time|date:"M d, Y" }}</td>
                    <td>
                      <a href="{% url 'dashboard:activity_detail' course.pk %}" class="btn btn-sm btn-warning">
                        <i class="fas fa-eye"></i> View
                      </a>
                    </td>
                  </tr>
                  {% endfor %}
                </tbody>
              </table>
            </div>
          </div>
        </div>
        {% endif %}
        
        <!-- Videos Results -->
        {% if videos %}
        <div class="app-card app-card-orders-table shadow-sm mb-4">
          <div class="app-card-header p-3">
            <div class="row align-items-center">
              <div class="col">
                <h4 class="app-card-title mb-0">
                  <i class="fas fa-play-circle text-danger me-2"></i>
                  Videos ({{ videos|length }})
                </h4>
              </div>
            </div>
          </div>
          <div class="app-card-body">
            <div class="table-responsive">
              <table class="table table-hover mb-0">
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Description</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {% for video in videos %}
                  <tr>
                    <td>{{ video.title }}</td>
                    <td>{{ video.description|truncatewords:10 }}</td>
                    <td>
                      <a href="{% url 'dashboard:video_detail' video.pk %}" class="btn btn-sm btn-danger">
                        <i class="fas fa-eye"></i> View
                      </a>
                    </td>
                  </tr>
                  {% endfor %}
                </tbody>
              </table>
            </div>
          </div>
        </div>
        {% endif %}
        
        <!-- No Results -->
        {% if not students and not teachers and not courses and not subjects and not levels and not streams and not videos and not live_classes and not enrollments %}
        <div class="alert alert-warning">
          <div class="text-center py-5">
            <i class="fas fa-search fa-3x text-muted mb-3"></i>
            <h4>No Results Found</h4>
            <p class="text-muted">Try adjusting your search query or use different keywords.</p>
          </div>
        </div>
        {% endif %}
        
      {% else %}
        <div class="alert alert-info">
          <div class="text-center py-5">
            <i class="fas fa-info-circle fa-3x text-muted mb-3"></i>
            <h4>Start Searching</h4>
            <p class="text-muted">Enter a search query in the search bar above.</p>
            <p class="mb-0">
              <strong>Pro Tips:</strong><br>
              • Search by name, username, email, or phone<br>
              • Use <code>user:john</code> to search only users<br>
              • Use <code>student:jane</code> to search only students<br>
              • Use <code>course:physics</code> to search only courses<br>
              • And many more prefixes available!
            </p>
          </div>
        </div>
      {% endif %}
      
    </div><!--//container-fluid-->
  </div><!--//app-content-->
</div><!--//app-wrapper-->
{% endblock %}
```

---

## Usage

### Basic Search

Simply type your query in the search bar and press Enter:

```
physics
```

This will search across **all** categories for the term "physics".

### Prefix-Based Search

Use a prefix followed by a colon to search specific categories:

```
student:john        # Search only students
teacher:smith       # Search only teachers
course:physics      # Search only courses
subject:math        # Search only subjects
video:tutorial      # Search only videos
live:quantum        # Search only live classes
level:grade         # Search only academic levels
stream:science      # Search only streams
enrollment:john     # Search only enrollments
```

### Keyboard Shortcuts

- **`/`** - Focus the search bar
- **`ESC`** - Clear and blur the search bar
- **`Enter`** - Submit the search

---

## Customization

### 1. Adding More Categories

To add a new category to search:

1. **Add to prefix_map** in the view:

```python
prefix_map = {
    # ... existing prefixes ...
    'newcategory': 'new_category',
}
```

2. **Add the search query**:

```python
if search_all or search_type == 'new_category':
    results['new_category'] = list(models.NewModel.objects.filter(
        Q(field1__icontains=search_term) |
        Q(field2__icontains=search_term)
    )[:20])
```

3. **Add to template** (`search_results.html`):

```html
{% if new_category %}
<div class="app-card app-card-orders-table shadow-sm mb-4">
  <div class="app-card-header p-3">
    <div class="row align-items-center">
      <div class="col">
        <h4 class="app-card-title mb-0">
          <i class="fas fa-icon text-color me-2"></i>
          Category Name ({{ new_category|length }})
        </h4>
      </div>
    </div>
  </div>
  <div class="app-card-body">
    <div class="table-responsive">
      <table class="table table-hover mb-0">
        <thead>
          <tr>
            <th>Column 1</th>
            <th>Column 2</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {% for item in new_category %}
          <tr>
            <td>{{ item.field1 }}</td>
            <td>{{ item.field2 }}</td>
            <td>
              <a href="{% url 'dashboard:detail_view' item.pk %}" class="btn btn-sm btn-primary">
                <i class="fas fa-eye"></i> View
              </a>
            </td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>
</div>
{% endif %}
```

### 2. Changing Result Limit

Change the `[:20]` slice to any number:

```python
results['students'] = list(models.User.objects.filter(
    # ... filters ...
)[:50])  # Change 20 to 50 for more results
```

### 3. Customizing Search Fields

Modify the Q objects to search different fields:

```python
# Search by different fields
results['students'] = list(models.User.objects.filter(
    Q(username__icontains=search_term) |
    Q(student_id__icontains=search_term) |  # Add student_id
    Q(phone__icontains=search_term)
)[:20])
```

### 4. Changing Colors

Update the color classes in the template:

```html
<!-- Change from text-success to text-primary -->
<i class="fas fa-user-graduate text-primary me-2"></i>

<!-- Change button color -->
<a href="#" class="btn btn-sm btn-primary">  <!-- was btn-success -->
```

### 5. Adding Pagination

To add pagination, modify the view:

```python
from django.core.paginator import Paginator

def global_search_view(request):
    # ... existing code ...
    
    # Paginate results
    students = models.User.objects.filter(...)  # Don't slice yet
    paginator = Paginator(students, 20)  # 20 per page
    page_number = request.GET.get('page')
    results['students'] = paginator.get_page(page_number)
```

---

## Troubleshooting

### Issue: NoReverseMatch Error

**Problem**: URL pattern not found (e.g., `course_detail`)

**Solution**: Check your URL patterns and update the template:

```python
# In urls.py
path('activities/<int:pk>/', views.activity_detail, name='activity_detail'),

# In template
{% url 'dashboard:activity_detail' course.pk %}  # Not 'course_detail'
```

### Issue: FieldError - Cannot resolve keyword 'name'

**Problem**: Searching for a field that doesn't exist in the model

**Solution**: Check your model fields and update the query:

```python
# Check model first
class Course(models.Model):
  title = models.CharField(...)  # Field is 'title', not 'name'

# Update query
Q(title__icontains=search_term)  # Not 'name'
```

### Issue: Search returns no results

**Checklist**:
1. ✅ Verify data exists in database
2. ✅ Check if `search_all` variable is set correctly
3. ✅ Ensure model imports are correct
4. ✅ Verify field names match your models
5. ✅ Check if results are converted to list: `list(...)`

### Issue: Search bar not showing

**Checklist**:
1. ✅ Verify Bootstrap and FontAwesome are loaded
2. ✅ Check CSS file is included
3. ✅ Ensure JavaScript is loaded at bottom of page
4. ✅ Check browser console for errors

---

## Performance Optimization

### 1. Add Database Indexes

```python
class Meta:
    indexes = [
        models.Index(fields=['username']),
        models.Index(fields=['first_name', 'last_name']),
        models.Index(fields=['email']),
    ]
```

### 2. Use select_related / prefetch_related

```python
results['students'] = list(models.User.objects.filter(
    # ... filters ...
).select_related('academic_level')[:20])
```

### 3. Implement Caching

```python
from django.core.cache import cache

def global_search_view(request):
    query = request.GET.get('q', '').strip()
    cache_key = f'search:{query}'
    
    # Try to get from cache
    results = cache.get(cache_key)
    if results:
        return render(request, 'dashboard/search_results.html', results)
    
    # ... perform search ...
    
    # Cache results for 5 minutes
    cache.set(cache_key, results, 300)
    
    return render(request, 'dashboard/search_results.html', results)
```

### 4. Use Full-Text Search (PostgreSQL)

```python
from django.contrib.postgres.search import SearchVector, SearchQuery

# In your view
search_query = SearchQuery(search_term)
results['students'] = list(models.User.objects.annotate(
    search=SearchVector('username', 'first_name', 'last_name', 'email')
).filter(search=search_query)[:20])
```

---

## Security Considerations

### 1. Authentication Required

The view uses `@login_required` decorator. Ensure you have authentication set up:

```python
# settings.py
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
```

### 2. SQL Injection Protection

Django's ORM automatically protects against SQL injection. **Never** use raw SQL for search:

```python
# ✅ GOOD - Uses ORM
models.User.objects.filter(username__icontains=search_term)

# ❌ BAD - Raw SQL vulnerable to injection
models.User.objects.raw(f"SELECT * FROM users WHERE username LIKE '%{search_term}%'")
```

### 3. Rate Limiting

Consider adding rate limiting to prevent abuse:

```python
from django.views.decorators.cache import cache_page

@cache_page(60)  # Cache for 60 seconds
@login_required
def global_search_view(request):
    # ... your code ...
```

Or use Django Ratelimit:

```bash
pip install django-ratelimit
```

```python
from ratelimit.decorators import ratelimit

@ratelimit(key='user', rate='10/m')  # 10 requests per minute
@login_required
def global_search_view(request):
    # ... your code ...
```

---

## Advanced Features

### 1. Search History

Save search history for users:

```python
class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

# In view
def global_search_view(request):
    # ... existing code ...
    
    # Save search history
    if query:
        SearchHistory.objects.create(user=request.user, query=query)
```

### 2. Autocomplete Suggestions

Add AJAX autocomplete:

```javascript
// In your JavaScript
const input = document.getElementById('global-search');
let debounceTimer;

input.addEventListener('input', (e) => {
  clearTimeout(debounceTimer);
  const query = e.target.value;
  
  debounceTimer = setTimeout(() => {
    if (query.length >= 3) {
      fetch(`/api/search/suggestions/?q=${encodeURIComponent(query)}`)
        .then(res => res.json())
        .then(data => {
          // Display suggestions
          showSuggestions(data.suggestions);
        });
    }
  }, 300);
});
```

### 3. Search Analytics

Track search metrics:

```python
class SearchAnalytics(models.Model):
    query = models.CharField(max_length=200)
    results_count = models.IntegerField()
    search_type = models.CharField(max_length=50, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

# In view
def global_search_view(request):
    # ... existing code ...
    
    # Track analytics
    total_results = sum(len(results[key]) for key in ['students', 'teachers', ...])
    SearchAnalytics.objects.create(
        query=query,
        results_count=total_results,
        search_type=search_type
    )
```

---

## Model Requirements

Your models should have these basic structures for the search to work:

### User Model
```python
class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        TEACHER = "teacher", "Teacher"
    
    role = models.CharField(max_length=10, choices=Role.choices)
    phone = models.CharField(max_length=20, blank=True, null=True)
    academic_level = models.ForeignKey('AcademicLevel', on_delete=models.SET_NULL, 
                                      blank=True, null=True, related_name='students')
```

### Course Model (Course)
```python
class Course(models.Model):
  title = models.CharField(max_length=200)
  description = models.TextField(blank=True)
  cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)
  start_time = models.DateTimeField()
  end_time = models.DateTimeField()
```

### Video Model
```python
class Video(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
```

### LiveClass Model
```python
class LiveClass(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
```

### Subject Model
```python
class Subject(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
```

### AcademicLevel Model
```python
class AcademicLevel(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
```

### Stream Model
```python
class Stream(models.Model):
    name = models.CharField(max_length=100, unique=True)
```

### Enrollment Model
```python
class Enrollment(models.Model):
    student = models.ForeignKey(User, related_name="enrollments", on_delete=models.CASCADE)
    level = models.ForeignKey(AcademicLevel, related_name="enrollments", on_delete=models.CASCADE)
    joined_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=False)
```

---

## Testing

### Unit Tests

```python
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class SearchViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_search_without_query(self):
        response = self.client.get(reverse('dashboard:global_search'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Start Searching')
    
    def test_search_with_query(self):
        response = self.client.get(reverse('dashboard:global_search'), {'q': 'test'})
        self.assertEqual(response.status_code, 200)
    
    def test_search_with_prefix(self):
        response = self.client.get(reverse('dashboard:global_search'), {'q': 'student:test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'students')
```

---

## License

This code is provided as-is for educational and commercial use. Feel free to modify and adapt it to your needs.

---

## Credits

Created by: **Kitwosd**  
Project: Durbar Physics Learning Management System  
Date: November 2025

---

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review Django documentation: https://docs.djangoproject.com/
3. Check Bootstrap documentation: https://getbootstrap.com/docs/

---

## Changelog

### Version 1.0.0 (November 2025)
- ✅ Initial release
- ✅ Multi-model search support
- ✅ Prefix-based filtering
- ✅ Keyboard shortcuts
- ✅ Responsive design
- ✅ Error handling
- ✅ Search analytics support

---

**Happy Searching! 🔍**
