from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from customer.models import Customer
from .models import CustomerContact


class CustomerContactModelTest(TestCase):
    """Test cases for CustomerContact model"""
    
    def setUp(self):
        """Set up test data"""
        self.customer = Customer.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            nic='123456789V'
        )
    
    def test_create_customer_contact(self):
        """Test creating a customer contact"""
        contact = CustomerContact.objects.create(
            customer=self.customer,
            email='contact@example.com',
            wa_number='+94771234567',
            tp_number='+94112345678',
            is_primary=True
        )
        
        self.assertEqual(contact.customer, self.customer)
        self.assertEqual(contact.email, 'contact@example.com')
        self.assertEqual(contact.wa_number, '+94771234567')
        self.assertEqual(contact.tp_number, '+94112345678')
        self.assertTrue(contact.is_primary)
        self.assertTrue(contact.is_active)  # Default value
    
    def test_contact_str_representation(self):
        """Test string representation of contact"""
        contact = CustomerContact.objects.create(
            customer=self.customer,
            email='contact@example.com',
            wa_number='+94771234567',
            tp_number='+94112345678'
        )
        
        expected_str = f"{self.customer.full_name} - contact@example.com"
        self.assertEqual(str(contact), expected_str)
    
    def test_contact_info_property(self):
        """Test contact_info property"""
        contact = CustomerContact.objects.create(
            customer=self.customer,
            email='contact@example.com',
            wa_number='+94771234567',
            tp_number='+94112345678',
            is_primary=True
        )
        
        expected_info = {
            'email': 'contact@example.com',
            'whatsapp': '+94771234567',
            'telephone': '+94112345678',
            'is_primary': True
        }
        
        self.assertEqual(contact.contact_info, expected_info)
    
    def test_primary_contact_uniqueness(self):
        """Test that only one contact can be primary per customer"""
        # Create first primary contact
        contact1 = CustomerContact.objects.create(
            customer=self.customer,
            email='contact1@example.com',
            wa_number='+94771234567',
            tp_number='+94112345678',
            is_primary=True
        )
        
        # Create second primary contact
        contact2 = CustomerContact.objects.create(
            customer=self.customer,
            email='contact2@example.com',
            wa_number='+94771234568',
            tp_number='+94112345679',
            is_primary=True
        )
        
        # Refresh from database
        contact1.refresh_from_db()
        contact2.refresh_from_db()
        
        # Only contact2 should be primary now
        self.assertFalse(contact1.is_primary)
        self.assertTrue(contact2.is_primary)


class CustomerContactAPITest(APITestCase):
    """Test cases for CustomerContact API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.customer = Customer.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            nic='123456789V'
        )
        
        # Get authentication token
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.access_token = response.data['data']['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_create_contact(self):
        """Test creating a contact via API"""
        url = reverse('customer_contact:contact_list_create')
        data = {
            'customer': self.customer.id,
            'email': 'api.test@example.com',
            'wa_number': '+94771234567',
            'tp_number': '+94112345678',
            'is_primary': True,
            'is_active': True
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['email'], 'api.test@example.com')
    
    def test_list_contacts(self):
        """Test listing contacts via API"""
        # Create a test contact
        CustomerContact.objects.create(
            customer=self.customer,
            email='list.test@example.com',
            wa_number='+94771234567',
            tp_number='+94112345678'
        )
        
        url = reverse('customer_contact:contact_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertGreater(len(response.data['data']), 0)
    
    def test_get_contact_detail(self):
        """Test getting contact detail via API"""
        contact = CustomerContact.objects.create(
            customer=self.customer,
            email='detail.test@example.com',
            wa_number='+94771234567',
            tp_number='+94112345678'
        )
        
        url = reverse('customer_contact:contact_detail', kwargs={'pk': contact.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['id'], contact.id)
    
    def test_update_contact(self):
        """Test updating contact via API"""
        contact = CustomerContact.objects.create(
            customer=self.customer,
            email='update.test@example.com',
            wa_number='+94771234567',
            tp_number='+94112345678'
        )
        
        url = reverse('customer_contact:contact_detail', kwargs={'pk': contact.id})
        data = {
            'email': 'updated.test@example.com',
            'wa_number': '+94771234568',
            'tp_number': '+94112345679'
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['email'], 'updated.test@example.com')
    
    def test_delete_contact(self):
        """Test deleting contact via API"""
        contact = CustomerContact.objects.create(
            customer=self.customer,
            email='delete.test@example.com',
            wa_number='+94771234567',
            tp_number='+94112345678'
        )
        
        url = reverse('customer_contact:contact_detail', kwargs={'pk': contact.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CustomerContact.objects.filter(id=contact.id).exists())
    
    def test_get_customer_contacts(self):
        """Test getting contacts for a specific customer via API"""
        CustomerContact.objects.create(
            customer=self.customer,
            email='customer.test@example.com',
            wa_number='+94771234567',
            tp_number='+94112345678'
        )
        
        url = reverse('customer_contact:customer_contacts', kwargs={'customer_id': self.customer.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['customer']['id'], self.customer.id)
        self.assertGreater(len(response.data['data']['contacts']), 0)
    
    def test_set_primary_contact(self):
        """Test setting contact as primary via API"""
        contact = CustomerContact.objects.create(
            customer=self.customer,
            email='primary.test@example.com',
            wa_number='+94771234567',
            tp_number='+94112345678',
            is_primary=False
        )
        
        url = reverse('customer_contact:set_primary_contact', kwargs={'contact_id': contact.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertTrue(response.data['data']['is_primary'])
    
    def test_toggle_contact_status(self):
        """Test toggling contact status via API"""
        contact = CustomerContact.objects.create(
            customer=self.customer,
            email='toggle.test@example.com',
            wa_number='+94771234567',
            tp_number='+94112345678',
            is_active=True
        )
        
        url = reverse('customer_contact:toggle_contact_status', kwargs={'contact_id': contact.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertFalse(response.data['data']['is_active'])  # Should be toggled to False
    
    def test_contact_statistics(self):
        """Test getting contact statistics via API"""
        CustomerContact.objects.create(
            customer=self.customer,
            email='stats.test@example.com',
            wa_number='+94771234567',
            tp_number='+94112345678'
        )
        
        url = reverse('customer_contact:contact_statistics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('total_contacts', response.data['data'])
        self.assertIn('active_contacts', response.data['data'])
