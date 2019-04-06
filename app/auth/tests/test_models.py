"""Tests for authentication models."""

import unittest
from app import db
from app.auth.models import Admin
from app.tests.test_utils import ModelTestMixin

class TestAdminModel(ModelTestMixin, unittest.TestCase):
    """Test the admin model."""

    def test_admin_creation(self):
        """Test creating an admin."""

        admin = Admin(
            first_name='Paul',
            last_name='Revere',
            email='paul@rider.com'
        )

        admin.set_password('mypassword')

        db.session.add(admin)
        db.session.commit()

        admin_db = Admin.query.first()

        self.assertEqual(admin, admin_db)
        self.assertEqual('paul@rider.com', admin_db.email)

        self.assertTrue(admin.check_password('mypassword'))
        self.assertFalse(admin.check_password('xmypassword'))
