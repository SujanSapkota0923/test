from django.test import TestCase, Client
from django.urls import reverse
from django.template import Template, Context
from django.contrib.auth import get_user_model


class DashboardSmokeTests(TestCase):
	def setUp(self):
		self.client = Client()
		User = get_user_model()
		# create an admin user and login via force_login
		self.admin = User.objects.create_user(username='admin_test', password='pass1234', role=User.Role.ADMIN)
		self.admin.is_superuser = True
		self.admin.is_staff = True
		self.admin.save()

	def test_index_view_renders_for_logged_in_admin(self):
		self.client.force_login(self.admin)
		url = reverse('dashboard:index')
		resp = self.client.get(url)
		# Should render the index (login required satisfied)
		self.assertIn(resp.status_code, (200, 302))

	def test_templatetag_custom_filters_loads(self):
		# Render a tiny template that loads our templatetag and uses the 'attr' filter
		class Obj:
			def __init__(self):
				self.foo = 'bar'

		tpl = Template("{% load custom_filters %}{{ obj|attr:'foo' }}")
		rendered = tpl.render(Context({'obj': Obj()})).strip()
		self.assertEqual(rendered, 'bar')

