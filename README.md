# Tender Management System

A comprehensive Django-based tender management platform for organizations to publish tenders and vendors to submit bids. The system supports various tender types including government procurement, military contracts, construction projects, educational supplies, healthcare equipment, and more.

## 🚀 Features

### Core Functionality
- **Multi-Organization Support**: Government agencies, private companies, military, schools, healthcare, NGOs, municipalities
- **Comprehensive Tender Management**: Create, publish, amend, and manage tenders
- **Vendor Registration & Verification**: Complete vendor profiles with verification system
- **Bid Submission & Management**: Technical and financial proposals with document uploads
- **Evaluation System**: Structured bid evaluation with scoring mechanisms
- **Contract Management**: Award contracts and track milestones
- **Payment Tracking**: Milestone-based payment system
- **Document Management**: Upload and manage tender and bid documents
- **Clarification System**: Q&A between vendors and organizations
- **Notifications**: Real-time notifications for all stakeholders
- **Review System**: Post-contract performance reviews and ratings

### Key Features
- ✅ SEO-friendly URLs with slugs
- ✅ UUID primary keys for enhanced security
- ✅ Comprehensive status tracking
- ✅ Multiple procurement methods (open, restricted, negotiated, etc.)
- ✅ Multi-currency support
- ✅ Document version control through amendments
- ✅ Vendor blacklisting and verification
- ✅ Rating and review system
- ✅ Advanced admin interface with statistics
- ✅ Hierarchical category system

## 📋 Requirements

```
Python >= 3.8
Django >= 4.2
PostgreSQL >= 12 (recommended) or SQLite for development
Pillow >= 10.0 (for image handling)
```

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/tender-management-system.git
cd tender-management-system
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=tender_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password

# Media and Static Files
MEDIA_URL=/media/
STATIC_URL=/static/
```

### 5. Database Setup
```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 6. Load Initial Data (Optional)
```bash
# Create tender categories
python manage.py shell
```

```python
from tenders.models import TenderCategory

categories = [
    ('Construction & Infrastructure', 'construction-infrastructure'),
    ('Information Technology', 'information-technology'),
    ('Medical & Healthcare Supplies', 'medical-healthcare-supplies'),
    ('Military & Defense Equipment', 'military-defense-equipment'),
    ('Office Supplies & Equipment', 'office-supplies-equipment'),
    ('Educational Materials', 'educational-materials'),
    ('Food & Catering Services', 'food-catering-services'),
    ('Security Services', 'security-services'),
    ('Consulting Services', 'consulting-services'),
    ('Vehicles & Transportation', 'vehicles-transportation'),
    ('Furniture & Fixtures', 'furniture-fixtures'),
    ('Cleaning Services', 'cleaning-services'),
    ('Printing Services', 'printing-services'),
    ('Uniforms & Garments', 'uniforms-garments'),
    ('Research & Development', 'research-development'),
]

for name, slug in categories:
    TenderCategory.objects.create(name=name, slug=slug)
```

### 7. Run Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/admin/` to access the admin panel.

## 📁 Project Structure

```
tender-management-system/
├── manage.py
├── requirements.txt
├── README.md
├── .env
├── .gitignore
│
├── config/                      # Project configuration
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── tenders/                     # Main app
│   ├── __init__.py
│   ├── models.py                # All models
│   ├── admin.py                 # Admin configuration
│   ├── views.py                 # Views
│   ├── urls.py                  # URL patterns
│   ├── forms.py                 # Forms
│   ├── serializers.py           # DRF serializers (optional)
│   ├── signals.py               # Django signals
│   ├── utils.py                 # Utility functions
│   ├── managers.py              # Custom model managers
│   ├── permissions.py           # Custom permissions
│   │
│   ├── migrations/              # Database migrations
│   │   └── __init__.py
│   │
│   ├── templates/               # Templates
│   │   └── tenders/
│   │       ├── tender_list.html
│   │       ├── tender_detail.html
│   │       ├── bid_form.html
│   │       └── ...
│   │
│   └── static/                  # Static files
│       └── tenders/
│           ├── css/
│           ├── js/
│           └── images/
│
├── media/                       # Uploaded files
│   ├── organizations/
│   │   └── logos/
│   ├── tender_documents/
│   ├── bid_documents/
│   ├── vendor_documents/
│   ├── contracts/
│   ├── amendments/
│   ├── milestone_verifications/
│   └── payment_receipts/
│
└── static/                      # Collected static files
    ├── admin/
    ├── css/
    ├── js/
    └── images/
```

## 🗄️ Database Models

### Organization Model
Organizations that post tenders (Government, Private, Military, Schools, etc.)
- Basic info with logo
- Registration and tax details
- Contact information
- Verification status

### Tender Model
Core tender/procurement model with:
- Multiple procurement methods
- Financial details with multi-currency
- Eligibility criteria
- Important dates and deadlines
- Project location
- Status tracking (draft, published, ongoing, closed, awarded, cancelled)

### Vendor Model
Companies/vendors that bid on tenders:
- Business registration details
- Capabilities and service areas
- Verification and blacklist status
- Rating system

### Bid Model
Vendor bids with:
- Technical and financial proposals
- Bid security
- Evaluation scores
- Status tracking

### Contract Model
Awarded contracts with:
- Contract value and duration
- Terms and conditions
- Performance bonds
- Milestone tracking
- Digital signatures

### Supporting Models
- **TenderCategory**: Hierarchical categorization
- **TenderDocument**: Tender-related documents
- **BidDocument**: Bid submission documents
- **TenderAmendment**: Amendments/addendums
- **Clarification**: Q&A system
- **Milestone**: Contract milestones and payments
- **Evaluation**: Bid evaluation framework
- **BidEvaluation**: Individual bid scores
- **Notification**: System notifications
- **Review**: Performance reviews

## 🔐 User Roles & Permissions

### Superadmin
- Full system access
- Manage all organizations and vendors
- System configuration

### Organization Admin
- Create and manage tenders
- Review and evaluate bids
- Award contracts
- Answer clarifications
- Manage organization profile

### Vendor
- Browse and search tenders
- Submit bids
- Upload documents
- Ask clarifications
- Track bid status
- Manage contracts

### Evaluator
- Access assigned tenders
- Evaluate bids
- Score proposals
- Provide recommendations

## 🎯 Usage Examples

### Creating a Tender
```python
from tenders.models import Tender, Organization, TenderCategory

# Get organization and category
org = Organization.objects.get(slug='ministry-of-defense')
category = TenderCategory.objects.get(slug='military-defense-equipment')

# Create tender
tender = Tender.objects.create(
    tender_number='MOD/2025/001',
    title='Procurement of Military Vehicles',
    organization=org,
    category=category,
    description='Supply of 50 armored personnel carriers',
    detailed_requirements='Full technical specifications...',
    status='published',
    procurement_method='open',
    estimated_value=5000000.00,
    currency='USD',
    publication_date=timezone.now(),
    submission_deadline=timezone.now() + timedelta(days=30),
    opening_date=timezone.now() + timedelta(days=31),
    project_location='National Defense Base',
    project_city='Nairobi',
    project_country='Kenya',
    eligible_countries='KE,UG,TZ,RW',
    minimum_experience_years=5,
    contact_person='John Doe',
    contact_email='procurement@mod.gov.ke',
    contact_phone='+254700000000'
)
```

### Submitting a Bid
```python
from tenders.models import Bid, Vendor, Tender

# Get vendor and tender
vendor = Vendor.objects.get(slug='acme-defense-systems')
tender = Tender.objects.get(tender_number='MOD/2025/001')

# Create bid
bid = Bid.objects.create(
    bid_number='BID-MOD-2025-001',
    tender=tender,
    vendor=vendor,
    bid_amount=4800000.00,
    currency='USD',
    technical_proposal='Our company has 10 years experience...',
    financial_proposal='Detailed cost breakdown...',
    delivery_timeline_days=180,
    bid_security_reference='BG-12345',
    bid_security_amount=240000.00,
    status='submitted',
    submitted_at=timezone.now()
)
```

### Awarding a Contract
```python
from tenders.models import Contract, Bid

# Get winning bid
winning_bid = Bid.objects.get(bid_number='BID-MOD-2025-001')
winning_bid.status = 'awarded'
winning_bid.save()

# Create contract
contract = Contract.objects.create(
    contract_number='CONTRACT/MOD/2025/001',
    tender=winning_bid.tender,
    winning_bid=winning_bid,
    vendor=winning_bid.vendor,
    contract_value=4800000.00,
    currency='USD',
    start_date=date.today(),
    end_date=date.today() + timedelta(days=365),
    duration_days=365,
    status='active',
    terms_and_conditions='Standard government contract terms...',
    performance_bond_amount=480000.00,
    retention_percentage=10.0
)
```

## 📊 Admin Interface Features

### Dashboard Statistics
- Total tenders (by status)
- Total bids received
- Active contracts
- Pending evaluations
- Revenue statistics

### Tender Management
- Bulk actions (publish, close, cancel, feature)
- Inline document management
- Amendment tracking
- Clarification management
- Bid statistics

### Vendor Management
- Verification workflow
- Blacklist management
- Rating overview
- Bid and contract history

### Bid Management
- Status updates
- Evaluation scores
- Document review
- Comparison tools

### Contract Management
- Milestone tracking
- Payment status
- Signature tracking
- Performance monitoring

## 🔔 Notifications

The system sends notifications for:
- New tender published
- Tender closing soon
- Bid submitted successfully
- Bid status changed
- Clarification answered
- Amendment published
- Contract awarded
- Milestone due
- Payment released

## 🛡️ Security Features

- UUID primary keys to prevent enumeration attacks
- Vendor verification system
- Blacklist functionality
- Document access control
- Audit trails (via timestamps)
- Secure file uploads
- Permission-based access

## 📈 Advanced Features

### Search & Filtering
```python
# Filter tenders by multiple criteria
tenders = Tender.objects.filter(
    status='published',
    category__slug='construction-infrastructure',
    submission_deadline__gte=timezone.now(),
    estimated_value__lte=1000000
)
```

### Tender Categories with Subcategories
```python
# Create parent category
parent = TenderCategory.objects.create(
    name='Construction',
    slug='construction'
)

# Create subcategories
TenderCategory.objects.create(
    name='Road Construction',
    slug='road-construction',
    parent=parent
)
```

### Custom Managers (Add to models.py)
```python
class PublishedTenderManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            status='published',
            submission_deadline__gte=timezone.now()
        )

# In Tender model
class Tender(models.Model):
    # ... existing fields ...
    objects = models.Manager()
    published = PublishedTenderManager()
```

## 🔧 API Development (Optional)

Add Django REST Framework for API endpoints:

```bash
pip install djangorestframework djangorestframework-simplejwt
```

Create `serializers.py`:
```python
from rest_framework import serializers
from .models import Tender, Bid, Vendor

class TenderSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Tender
        fields = '__all__'
        read_only_fields = ['slug', 'created_at', 'updated_at']
```

## 🧪 Testing

Create tests in `tests.py`:
```python
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Organization, Tender, Vendor, Bid

class TenderModelTest(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(
            name='Test Organization',
            organization_type='government',
            registration_number='REG001',
            email='test@org.com',
            phone='+254700000000',
            address='Test Address',
            city='Nairobi',
            country='Kenya'
        )
    
    def test_tender_creation(self):
        tender = Tender.objects.create(
            tender_number='TEST/2025/001',
            title='Test Tender',
            organization=self.org,
            # ... other fields
        )
        self.assertEqual(tender.status, 'draft')
        self.assertIsNotNone(tender.slug)
```

Run tests:
```bash
python manage.py test tenders
```

## 📱 Frontend Integration

### Template Context Processors
Add to `settings.py`:
```python
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                # ... default processors
                'tenders.context_processors.tender_stats',
            ],
        },
    },
]
```

Create `context_processors.py`:
```python
from .models import Tender, Bid

def tender_stats(request):
    return {
        'active_tenders_count': Tender.objects.filter(status='published').count(),
        'total_bids_count': Bid.objects.filter(status='submitted').count(),
    }
```

## 🚀 Deployment

### Production Settings
Create `settings_prod.py`:
```python
from .settings import *

DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
```

### Collect Static Files
```bash
python manage.py collectstatic
```

### Setup Gunicorn
```bash
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

## 📝 Requirements.txt

```txt
Django>=4.2,<5.0
Pillow>=10.0.0
psycopg2-binary>=2.9.5
python-decouple>=3.8
django-crispy-forms>=2.0
crispy-bootstrap5>=0.7
djangorestframework>=3.14.0
djangorestframework-simplejwt>=5.2.2
django-filter>=23.2
celery>=5.3.0
redis>=4.5.0
gunicorn>=21.2.0
whitenoise>=6.5.0
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Support

For support, email support@tendersystem.com or open an issue on GitHub.

## 🎉 Acknowledgments

- Django Documentation
- Django Admin Documentation
- Contributors and testers

---

**Made with Love  for efficient tender management**