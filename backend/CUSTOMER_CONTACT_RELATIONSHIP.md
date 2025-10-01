# Customer-Contact Relationship Implementation

## Overview
Added comprehensive relationship methods between Customer and CustomerContact models to enable easy management of customer contact information.

## Relationship Structure

### Database Relationship
- **CustomerContact** has a ForeignKey to **Customer** with `related_name='contacts'`
- This creates a one-to-many relationship: One Customer → Many CustomerContacts

### Customer Model Enhancements

#### 1. Contact Retrieval Methods
```python
# Get all active contacts for a customer
customer.get_contacts()

# Get the primary contact for a customer
customer.get_primary_contact()

# Get contact summary with all details
customer.get_contact_summary()
```

#### 2. Contact Management Methods
```python
# Add a new contact
customer.add_contact(
    email="contact@example.com",
    wa_number="+94771234567", 
    tp_number="+94112345678",
    is_primary=True
)

# Update primary contact
customer.update_primary_contact(contact_id=1)
```

#### 3. Convenient Properties
```python
# Get primary contact details with fallbacks
customer.primary_email      # Primary contact email or customer email
customer.primary_whatsapp   # Primary contact WhatsApp
customer.primary_telephone  # Primary contact telephone or customer phone
```

#### 4. Data Synchronization
- When customer email is updated, it automatically updates the primary contact email
- Ensures data consistency between Customer and CustomerContact models

## Usage Examples

### Creating a Customer with Contacts
```python
# Create a customer
customer = Customer.objects.create(
    nic="123456789V",
    first_name="John",
    last_name="Doe",
    email="john.doe@example.com",
    phone_number="0771234567"
)

# Add contacts
customer.add_contact(
    email="john.doe@example.com",
    wa_number="0771234567",
    tp_number="0112345678",
    is_primary=True
)

customer.add_contact(
    email="john.work@company.com", 
    wa_number="0779876543",
    tp_number="0117654321",
    is_primary=False
)
```

### Accessing Contact Information
```python
# Get all contacts
contacts = customer.get_contacts()
print(f"Customer has {contacts.count()} contacts")

# Get primary contact
primary = customer.get_primary_contact()
if primary:
    print(f"Primary email: {primary.email}")
    print(f"Primary WhatsApp: {primary.wa_number}")

# Get contact summary
summary = customer.get_contact_summary()
print(summary)
# Output:
# {
#     'total_contacts': 2,
#     'primary_contact': {
#         'email': 'john.doe@example.com',
#         'whatsapp': '0771234567',
#         'telephone': '0112345678'
#     },
#     'all_contacts': [...]
# }
```

### Using Properties
```python
# These properties provide fallbacks
print(customer.primary_email)      # Primary contact email or customer.email
print(customer.primary_whatsapp)   # Primary contact WhatsApp or None
print(customer.primary_telephone)  # Primary contact phone or customer.phone_number
```

## API Integration

### Serializer Updates
You can now include contact information in your Customer serializer:

```python
class CustomerSerializer(serializers.ModelSerializer):
    contacts = CustomerContactSerializer(many=True, read_only=True)
    primary_contact = CustomerContactSerializer(read_only=True)
    contact_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = Customer
        fields = '__all__'
    
    def get_contact_summary(self, obj):
        return obj.get_contact_summary()
```

### API Endpoints
The relationship enables these API patterns:

```python
# Get customer with all contacts
GET /api/customers/1/?include_contacts=true

# Get customer contact summary  
GET /api/customers/1/contact-summary/

# Add contact to customer
POST /api/customers/1/contacts/

# Update primary contact
PATCH /api/customers/1/set-primary-contact/
```

## Migration Steps

### To Apply These Changes:

1. **Apply customer migration**:
   ```bash
   python manage.py migrate customer 0001
   ```

2. **Apply customer_contact migration**:
   ```bash
   python manage.py migrate customer_contact 0002
   ```

3. **Apply all remaining migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Verify migration status**:
   ```bash
   python manage.py showmigrations
   ```

## Benefits

### 1. **Data Consistency**
- Automatic synchronization between customer and contact emails
- Primary contact management with constraints

### 2. **Easy Access**
- Convenient methods to access contact information
- Properties with intelligent fallbacks

### 3. **Flexible Contact Management**
- Support for multiple contacts per customer
- Primary contact designation
- Active/inactive contact status

### 4. **API-Ready**
- Methods return data in API-friendly formats
- Easy integration with Django REST Framework serializers

## Database Schema

After migrations, you'll have:

### customers table
- Basic customer information
- Related to customer_contacts via ForeignKey

### customer_contacts table  
- Multiple contacts per customer
- Foreign key to customers table
- Primary contact designation
- Unique constraints for email/phone combinations per customer

This relationship structure provides a robust foundation for managing customer contact information while maintaining data integrity and providing convenient access methods.