from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import CustomerContact
from customer.models import Customer
from .serializers import (
    CustomerContactSerializer,
    CustomerContactCreateSerializer,
    CustomerContactUpdateSerializer,
    CustomerWithContactsSerializer
)


class CustomerContactListCreateView(generics.ListCreateAPIView):
    """
    API endpoint to list and create customer contacts
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CustomerContactCreateSerializer
        return CustomerContactSerializer
    
    def get_queryset(self):
        """
        Filter contacts based on query parameters
        """
        queryset = CustomerContact.objects.select_related('customer').all()
        
        # Filter by customer
        customer_id = self.request.query_params.get('customer_id', None)
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by primary status
        is_primary = self.request.query_params.get('is_primary', None)
        if is_primary is not None:
            queryset = queryset.filter(is_primary=is_primary.lower() == 'true')
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(email__icontains=search) |
                Q(wa_number__icontains=search) |
                Q(tp_number__icontains=search) |
                Q(customer__first_name__icontains=search) |
                Q(customer__last_name__icontains=search) |
                Q(customer__username__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """
        Create a new customer contact
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            contact = serializer.save()
            return Response({
                'success': True,
                'message': 'Customer contact created successfully',
                'data': CustomerContactSerializer(contact).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Contact creation failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request, *args, **kwargs):
        """
        List customer contacts with custom response format
        """
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)
            return Response({
                'success': True,
                'message': 'Contacts retrieved successfully',
                'data': paginated_response.data
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'Contacts retrieved successfully',
            'data': serializer.data
        })


class CustomerContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update, or delete a specific customer contact
    """
    queryset = CustomerContact.objects.select_related('customer').all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CustomerContactUpdateSerializer
        return CustomerContactSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific customer contact
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'message': 'Contact retrieved successfully',
            'data': serializer.data
        })
    
    def update(self, request, *args, **kwargs):
        """
        Update a specific customer contact
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            contact = serializer.save()
            return Response({
                'success': True,
                'message': 'Contact updated successfully',
                'data': CustomerContactSerializer(contact).data
            })
        
        return Response({
            'success': False,
            'message': 'Contact update failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a specific customer contact
        """
        instance = self.get_object()
        instance.delete()
        return Response({
            'success': True,
            'message': 'Contact deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)


class CustomerContactsByCustomerView(APIView):
    """
    API endpoint to get all contacts for a specific customer
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, customer_id):
        """
        Get all contacts for a specific customer
        """
        try:
            customer = Customer.objects.get(id=customer_id)
            contacts = CustomerContact.objects.filter(
                customer=customer
            ).order_by('-is_primary', '-created_at')
            
            serializer = CustomerContactSerializer(contacts, many=True)
            return Response({
                'success': True,
                'message': 'Customer contacts retrieved successfully',
                'data': {
                    'customer': {
                        'id': customer.id,
                        'customer_id': customer.customer_id,
                        'full_name': customer.full_name,
                        'username': customer.username
                    },
                    'contacts': serializer.data
                }
            })
        
        except Customer.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Customer not found'
            }, status=status.HTTP_404_NOT_FOUND)


class CustomerWithContactsListView(generics.ListAPIView):
    """
    API endpoint to list customers with their contacts
    """
    queryset = Customer.objects.prefetch_related('contacts').all()
    serializer_class = CustomerWithContactsSerializer
    permission_classes = [IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        """
        List customers with their contacts
        """
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)
            return Response({
                'success': True,
                'message': 'Customers with contacts retrieved successfully',
                'data': paginated_response.data
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'Customers with contacts retrieved successfully',
            'data': serializer.data
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_primary_contact(request, contact_id):
    """
    Set a contact as primary for the customer
    """
    try:
        contact = CustomerContact.objects.get(id=contact_id)
        
        # Set this contact as primary (will automatically unset others)
        contact.is_primary = True
        contact.save()
        
        return Response({
            'success': True,
            'message': 'Contact set as primary successfully',
            'data': CustomerContactSerializer(contact).data
        })
    
    except CustomerContact.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Contact not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_contact_status(request, contact_id):
    """
    Toggle active/inactive status of a contact
    """
    try:
        contact = CustomerContact.objects.get(id=contact_id)
        contact.is_active = not contact.is_active
        contact.save()
        
        status_text = "activated" if contact.is_active else "deactivated"
        
        return Response({
            'success': True,
            'message': f'Contact {status_text} successfully',
            'data': CustomerContactSerializer(contact).data
        })
    
    except CustomerContact.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Contact not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def contact_statistics(request):
    """
    Get contact statistics
    """
    total_contacts = CustomerContact.objects.count()
    active_contacts = CustomerContact.objects.filter(is_active=True).count()
    primary_contacts = CustomerContact.objects.filter(is_primary=True).count()
    customers_with_contacts = Customer.objects.filter(contacts__isnull=False).distinct().count()
    customers_without_contacts = Customer.objects.filter(contacts__isnull=True).count()
    
    return Response({
        'success': True,
        'data': {
            'total_contacts': total_contacts,
            'active_contacts': active_contacts,
            'inactive_contacts': total_contacts - active_contacts,
            'primary_contacts': primary_contacts,
            'customers_with_contacts': customers_with_contacts,
            'customers_without_contacts': customers_without_contacts,
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_create_contacts(request):
    """
    Bulk create contacts for multiple customers
    """
    contacts_data = request.data.get('contacts', [])
    
    if not contacts_data:
        return Response({
            'success': False,
            'message': 'No contacts data provided'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    created_contacts = []
    errors = []
    
    for i, contact_data in enumerate(contacts_data):
        serializer = CustomerContactCreateSerializer(data=contact_data)
        if serializer.is_valid():
            contact = serializer.save()
            created_contacts.append(CustomerContactSerializer(contact).data)
        else:
            errors.append({
                'index': i,
                'errors': serializer.errors
            })
    
    return Response({
        'success': len(errors) == 0,
        'message': f'Created {len(created_contacts)} contacts successfully',
        'data': {
            'created_contacts': created_contacts,
            'errors': errors
        }
    }, status=status.HTTP_201_CREATED if len(errors) == 0 else status.HTTP_207_MULTI_STATUS)
