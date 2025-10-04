"""
Django management command to seed the database with realistic tender data.
Place this file at: management/commands/seed_data.py
Run with: python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from datetime import timedelta
from decimal import Decimal
import random

from main_application.models import (
    Organization, TenderCategory, Tender, TenderDocument,
    Vendor, Bid, BidDocument, TenderAmendment, Clarification,
    Contract, Milestone, Evaluation, BidEvaluation, Notification, Review
)


class Command(BaseCommand):
    help = 'Seeds the database with realistic tender management data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()

        self.stdout.write('Starting data seeding...')
        
        # Create data in order
        users = self.create_users()
        categories = self.create_categories()
        organizations = self.create_organizations()
        vendors = self.create_vendors(users)
        tenders = self.create_tenders(organizations, categories, users)
        self.create_tender_documents(tenders)
        self.create_amendments(tenders)
        bids = self.create_bids(tenders, vendors)
        self.create_bid_documents(bids)
        self.create_clarifications(tenders, vendors)
        evaluations = self.create_evaluations(tenders, users)
        self.create_bid_evaluations(evaluations, bids)
        contracts = self.create_contracts(tenders, bids, vendors)
        self.create_milestones(contracts)
        self.create_reviews(contracts, users)
        self.create_notifications(users)

        self.stdout.write(self.style.SUCCESS('Successfully seeded database!'))

    def clear_data(self):
        """Clear existing data"""
        Review.objects.all().delete()
        Notification.objects.all().delete()
        BidEvaluation.objects.all().delete()
        Evaluation.objects.all().delete()
        Milestone.objects.all().delete()
        Contract.objects.all().delete()
        Clarification.objects.all().delete()
        BidDocument.objects.all().delete()
        Bid.objects.all().delete()
        TenderAmendment.objects.all().delete()
        TenderDocument.objects.all().delete()
        Tender.objects.all().delete()
        Vendor.objects.all().delete()
        Organization.objects.all().delete()
        TenderCategory.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

    def create_users(self):
        """Create users for testing"""
        self.stdout.write('Creating users...')
        
        users = []
        
        # Admin users
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='steve',
                email='admin@tenders.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            users.append(admin)

        # Organization managers
        org_managers = [
            ('john.doe', 'john.doe@gov.ke', 'John', 'Doe'),
            ('sarah.johnson', 'sarah.j@construction.com', 'Sarah', 'Johnson'),
            ('michael.chen', 'mchen@defense.mil', 'Michael', 'Chen'),
            ('emma.wilson', 'ewilson@healthcare.org', 'Emma', 'Wilson'),
        ]

        for username, email, first, last in org_managers:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='password123',
                    first_name=first,
                    last_name=last
                )
                users.append(user)

        # Vendor users
        vendor_users = [
            ('vendor1', 'vendor1@builders.com', 'James', 'Smith'),
            ('vendor2', 'vendor2@techsolutions.com', 'Linda', 'Brown'),
            ('vendor3', 'vendor3@supplies.co.ke', 'Robert', 'Davis'),
            ('vendor4', 'vendor4@engineering.com', 'Maria', 'Garcia'),
            ('vendor5', 'vendor5@contractors.net', 'David', 'Martinez'),
        ]

        for username, email, first, last in vendor_users:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='password123',
                    first_name=first,
                    last_name=last
                )
                users.append(user)

        self.stdout.write(f'Created {len(users)} users')
        return users

    def create_categories(self):
        """Create tender categories"""
        self.stdout.write('Creating categories...')
        
        categories_data = [
            ('Construction & Infrastructure', 'building', None),
            ('Roads & Highways', 'road', 'Construction & Infrastructure'),
            ('Buildings', 'office', 'Construction & Infrastructure'),
            ('Bridges & Tunnels', 'bridge', 'Construction & Infrastructure'),
            ('IT & Technology', 'computer', None),
            ('Software Development', 'code', 'IT & Technology'),
            ('Hardware & Equipment', 'server', 'IT & Technology'),
            ('Consulting Services', 'briefcase', None),
            ('Medical Equipment', 'medical', None),
            ('Office Supplies', 'pencil', None),
            ('Security Services', 'shield', None),
            ('Cleaning & Maintenance', 'broom', None),
            ('Transportation & Logistics', 'truck', None),
            ('Electrical Works', 'bolt', None),
            ('Plumbing & HVAC', 'wrench', None),
        ]

        categories = {}
        
        for name, icon, parent_name in categories_data:
            parent = categories.get(parent_name) if parent_name else None
            
            category, created = TenderCategory.objects.get_or_create(
                name=name,
                defaults={
                    'slug': slugify(name),
                    'icon': icon,
                    'parent': parent,
                    'description': f'{name} related tenders and procurement'
                }
            )
            categories[name] = category

        self.stdout.write(f'Created {len(categories)} categories')
        return list(categories.values())

    def create_organizations(self):
        """Create organizations"""
        self.stdout.write('Creating organizations...')
        
        orgs_data = [
            {
                'name': 'Kenya Roads Authority',
                'type': 'parastatal',
                'reg_num': 'KRA-2010-001',
                'email': 'tenders@kra.go.ke',
                'phone': '+254-20-8011000',
                'website': 'https://www.kra.go.ke',
                'city': 'Nairobi',
                'country': 'Kenya',
            },
            {
                'name': 'Ministry of Health',
                'type': 'government',
                'reg_num': 'MOH-GOK-1963',
                'email': 'procurement@health.go.ke',
                'phone': '+254-20-2717077',
                'website': 'https://www.health.go.ke',
                'city': 'Nairobi',
                'country': 'Kenya',
            },
            {
                'name': 'Nairobi City County',
                'type': 'municipality',
                'reg_num': 'NCC-2013-047',
                'email': 'tenders@nairobi.go.ke',
                'phone': '+254-20-2177000',
                'website': 'https://www.nairobi.go.ke',
                'city': 'Nairobi',
                'country': 'Kenya',
            },
            {
                'name': 'Kenya Power & Lighting Company',
                'type': 'parastatal',
                'reg_num': 'KPLC-1922-001',
                'email': 'procurement@kplc.co.ke',
                'phone': '+254-20-3201000',
                'website': 'https://www.kplc.co.ke',
                'city': 'Nairobi',
                'country': 'Kenya',
            },
            {
                'name': 'University of Nairobi',
                'type': 'education',
                'reg_num': 'UON-1956-001',
                'email': 'supplies@uonbi.ac.ke',
                'phone': '+254-20-4913000',
                'website': 'https://www.uonbi.ac.ke',
                'city': 'Nairobi',
                'country': 'Kenya',
            },
            {
                'name': 'Safaricom PLC',
                'type': 'private',
                'reg_num': 'SAF-PLC-1997',
                'email': 'procurement@safaricom.co.ke',
                'phone': '+254-722-000000',
                'website': 'https://www.safaricom.co.ke',
                'city': 'Nairobi',
                'country': 'Kenya',
            },
            {
                'name': 'Kenya Defence Forces',
                'type': 'military',
                'reg_num': 'KDF-MOD-1963',
                'email': 'supplies@mod.go.ke',
                'phone': '+254-20-2721660',
                'website': 'https://www.mod.go.ke',
                'city': 'Nairobi',
                'country': 'Kenya',
            },
            {
                'name': 'Red Cross Kenya',
                'type': 'ngo',
                'reg_num': 'KRCS-NGO-1965',
                'email': 'procurement@redcross.or.ke',
                'phone': '+254-20-3950000',
                'website': 'https://www.redcross.or.ke',
                'city': 'Nairobi',
                'country': 'Kenya',
            },
        ]

        organizations = []
        for data in orgs_data:
            org, created = Organization.objects.get_or_create(
                registration_number=data['reg_num'],
                defaults={
                    'name': data['name'],
                    'organization_type': data['type'],
                    'email': data['email'],
                    'phone': data['phone'],
                    'website': data['website'],
                    'address': f"{data['name']} Headquarters",
                    'city': data['city'],
                    'country': data['country'],
                    'is_verified': True,
                }
            )
            organizations.append(org)

        self.stdout.write(f'Created {len(organizations)} organizations')
        return organizations

    def create_vendors(self, users):
        """Create vendor companies"""
        self.stdout.write('Creating vendors...')
        
        vendors_data = [
            {
                'company': 'Premier Builders Ltd',
                'type': 'llc',
                'reg_num': 'PB-2015-0123',
                'tax_id': 'TAX-PB-2015',
                'email': 'info@premierbuilders.co.ke',
                'phone': '+254-722-111111',
                'city': 'Nairobi',
                'year': 2015,
                'employees': 150,
                'turnover': 50000000,
            },
            {
                'company': 'TechSolutions Africa',
                'type': 'llc',
                'reg_num': 'TSA-2018-0456',
                'tax_id': 'TAX-TSA-2018',
                'email': 'contact@techsolutions.co.ke',
                'phone': '+254-733-222222',
                'city': 'Nairobi',
                'year': 2018,
                'employees': 45,
                'turnover': 15000000,
            },
            {
                'company': 'East Africa Supplies Co.',
                'type': 'corporation',
                'reg_num': 'EAS-2010-0789',
                'tax_id': 'TAX-EAS-2010',
                'email': 'sales@easupplies.co.ke',
                'phone': '+254-744-333333',
                'city': 'Mombasa',
                'year': 2010,
                'employees': 80,
                'turnover': 30000000,
            },
            {
                'company': 'Modern Engineering Ltd',
                'type': 'llc',
                'reg_num': 'MEL-2012-1011',
                'tax_id': 'TAX-MEL-2012',
                'email': 'info@moderneng.co.ke',
                'phone': '+254-755-444444',
                'city': 'Kisumu',
                'year': 2012,
                'employees': 120,
                'turnover': 40000000,
            },
            {
                'company': 'Swift Contractors Inc',
                'type': 'corporation',
                'reg_num': 'SCI-2016-1213',
                'tax_id': 'TAX-SCI-2016',
                'email': 'contracts@swiftcontractors.net',
                'phone': '+254-766-555555',
                'city': 'Nakuru',
                'year': 2016,
                'employees': 95,
                'turnover': 35000000,
            },
        ]

        vendors = []
        vendor_users = [u for u in users if u.username.startswith('vendor')]
        
        for i, data in enumerate(vendors_data):
            if i < len(vendor_users):
                vendor, created = Vendor.objects.get_or_create(
                    registration_number=data['reg_num'],
                    defaults={
                        'user': vendor_users[i],
                        'company_name': data['company'],
                        'business_type': data['type'],
                        'tax_id': data['tax_id'],
                        'email': data['email'],
                        'phone': data['phone'],
                        'address': f"{data['company']} Business Park",
                        'city': data['city'],
                        'country': 'Kenya',
                        'postal_code': f'00{100 + i}00',
                        'year_established': data['year'],
                        'number_of_employees': data['employees'],
                        'annual_turnover': data['turnover'],
                        'service_areas': 'Kenya, Uganda, Tanzania',
                        'is_verified': True,
                        'rating': Decimal(str(round(random.uniform(3.5, 5.0), 2))),
                        'total_reviews': random.randint(5, 50),
                    }
                )
                vendors.append(vendor)

        self.stdout.write(f'Created {len(vendors)} vendors')
        return vendors

    def create_tenders(self, organizations, categories, users):
        """Create tenders"""
        self.stdout.write('Creating tenders...')
        
        tenders_data = [
            {
                'number': 'KRA/RD/2025/001',
                'title': 'Construction of 50km Nairobi-Nakuru Highway Section',
                'org_idx': 0,
                'cat_name': 'Roads & Highways',
                'description': 'Design and construction of dual carriageway highway section including drainage, signage, and safety features',
                'requirements': 'Contractor must have completed at least 3 highway projects of minimum 30km. ISO 9001 certified. Equipment list required.',
                'value': 2500000000,
                'method': 'open',
                'duration': 720,
                'location': 'Nairobi-Nakuru Highway',
                'city': 'Kiambu',
                'min_exp': 10,
                'status': 'published',
            },
            {
                'number': 'MOH/MED/2025/012',
                'title': 'Supply and Installation of MRI Machines (5 Units)',
                'org_idx': 1,
                'cat_name': 'Medical Equipment',
                'description': 'Supply, installation, and commissioning of 5 MRI machines for county hospitals',
                'requirements': 'Must be authorized dealer. Provide 5-year warranty and training. Full maintenance package required.',
                'value': 750000000,
                'method': 'restricted',
                'duration': 180,
                'location': 'Multiple County Hospitals',
                'city': 'Nairobi',
                'min_exp': 5,
                'status': 'published',
            },
            {
                'number': 'NCC/IT/2025/003',
                'title': 'County Integrated Revenue Management System',
                'org_idx': 2,
                'cat_name': 'Software Development',
                'description': 'Development of cloud-based revenue collection and management system with mobile integration',
                'requirements': 'Experience in government systems. Must demonstrate similar implementations. Team of minimum 8 developers required.',
                'value': 150000000,
                'method': 'competitive_dialogue',
                'duration': 365,
                'location': 'City Hall, Nairobi',
                'city': 'Nairobi',
                'min_exp': 7,
                'status': 'ongoing',
            },
            {
                'number': 'KPLC/EL/2025/018',
                'title': 'Installation of 10,000 Smart Meters',
                'org_idx': 3,
                'cat_name': 'Electrical Works',
                'description': 'Supply and installation of prepaid smart electricity meters across Nairobi region',
                'requirements': 'EPRA certified electrical contractor. Previous smart meter installation experience mandatory.',
                'value': 180000000,
                'method': 'open',
                'duration': 240,
                'location': 'Greater Nairobi Area',
                'city': 'Nairobi',
                'min_exp': 5,
                'status': 'published',
            },
            {
                'number': 'UON/BUILD/2025/005',
                'title': 'Construction of Student Hostel (500 Capacity)',
                'org_idx': 4,
                'cat_name': 'Buildings',
                'description': 'Design and construction of modern student accommodation facility with amenities',
                'requirements': 'Experience in institutional buildings. NCA 1 registration. Previous hostel construction portfolio required.',
                'value': 450000000,
                'method': 'open',
                'duration': 540,
                'location': 'University of Nairobi, Main Campus',
                'city': 'Nairobi',
                'min_exp': 8,
                'status': 'published',
            },
            {
                'number': 'SAF/IT/2025/009',
                'title': 'Network Infrastructure Upgrade',
                'org_idx': 5,
                'cat_name': 'Hardware & Equipment',
                'description': 'Supply and installation of core network equipment for 50 base stations',
                'requirements': 'Cisco or Huawei certified partner. Provide equipment specs and compliance certificates.',
                'value': 320000000,
                'method': 'restricted',
                'duration': 180,
                'location': 'Multiple Sites Nationwide',
                'city': 'Nairobi',
                'min_exp': 6,
                'status': 'ongoing',
            },
            {
                'number': 'KDF/SEC/2025/022',
                'title': 'Supply of Security Surveillance Systems',
                'org_idx': 6,
                'cat_name': 'Security Services',
                'description': 'High-tech surveillance systems for military installations including AI-powered analytics',
                'requirements': 'Top Secret security clearance required. Must be registered defense contractor.',
                'value': 280000000,
                'method': 'negotiated',
                'duration': 270,
                'location': 'Multiple Military Bases',
                'city': 'Nairobi',
                'min_exp': 10,
                'status': 'ongoing',
            },
            {
                'number': 'KRCS/CONSULT/2025/004',
                'title': 'Disaster Preparedness Strategy Development',
                'org_idx': 7,
                'cat_name': 'Consulting Services',
                'description': 'Comprehensive disaster response and preparedness strategy for East Africa region',
                'requirements': 'International disaster management certification. Previous NGO consulting experience.',
                'value': 25000000,
                'method': 'framework',
                'duration': 120,
                'location': 'Red Cross Headquarters',
                'city': 'Nairobi',
                'min_exp': 8,
                'status': 'published',
            },
            {
                'number': 'KRA/BRIDGE/2025/007',
                'title': 'Construction of Nyali Bridge Expansion',
                'org_idx': 0,
                'cat_name': 'Bridges & Tunnels',
                'description': 'Expansion of existing bridge with additional lanes and pedestrian walkway',
                'requirements': 'Bridge construction specialist. Structural engineering certification. Marine construction experience.',
                'value': 1200000000,
                'method': 'open',
                'duration': 480,
                'location': 'Nyali, Mombasa',
                'city': 'Mombasa',
                'min_exp': 12,
                'status': 'closed',
            },
            {
                'number': 'NCC/CLEAN/2025/011',
                'title': 'City Cleaning and Waste Management Services',
                'org_idx': 2,
                'cat_name': 'Cleaning & Maintenance',
                'description': '24-month contract for city cleaning, waste collection, and disposal services',
                'requirements': 'Fleet of minimum 20 trucks. NEMA compliance certificate. Previous municipal contract required.',
                'value': 380000000,
                'method': 'open',
                'duration': 730,
                'location': 'Nairobi Central Business District',
                'city': 'Nairobi',
                'min_exp': 5,
                'status': 'awarded',
            },
        ]

        tenders = []
        now = timezone.now()
        
        for data in tenders_data:
            category = TenderCategory.objects.filter(name=data['cat_name']).first()
            org = organizations[data['org_idx']]
            
            # Calculate dates based on status
            if data['status'] == 'published':
                pub_date = now - timedelta(days=random.randint(5, 15))
                sub_deadline = now + timedelta(days=random.randint(15, 45))
            elif data['status'] == 'ongoing':
                pub_date = now - timedelta(days=random.randint(30, 60))
                sub_deadline = now + timedelta(days=random.randint(5, 15))
            elif data['status'] == 'closed':
                pub_date = now - timedelta(days=random.randint(90, 120))
                sub_deadline = now - timedelta(days=random.randint(15, 30))
            else:  # awarded
                pub_date = now - timedelta(days=random.randint(150, 200))
                sub_deadline = now - timedelta(days=random.randint(120, 150))
            
            opening_date = sub_deadline + timedelta(days=2)
            
            tender, created = Tender.objects.get_or_create(
                tender_number=data['number'],
                defaults={
                    'title': data['title'],
                    'organization': org,
                    'category': category,
                    'description': data['description'],
                    'detailed_requirements': data['requirements'],
                    'status': data['status'],
                    'procurement_method': data['method'],
                    'estimated_value': data['value'],
                    'currency': 'KES',
                    'bid_security_amount': Decimal(str(data['value'] * 0.02)),
                    'publication_date': pub_date,
                    'submission_deadline': sub_deadline,
                    'opening_date': opening_date,
                    'contract_duration_days': data['duration'],
                    'project_location': data['location'],
                    'project_city': data['city'],
                    'project_country': 'Kenya',
                    'eligible_countries': 'KE,UG,TZ,RW,BI',
                    'minimum_experience_years': data['min_exp'],
                    'minimum_turnover': Decimal(str(data['value'] * 0.3)),
                    'requires_prequalification': data['value'] > 1000000000,
                    'contact_person': f"{org.name} Procurement Officer",
                    'contact_email': org.email,
                    'contact_phone': org.phone,
                    'views_count': random.randint(50, 500),
                    'is_featured': random.choice([True, False]),
                    'created_by': random.choice(users[:4]),
                }
            )
            tenders.append(tender)

        self.stdout.write(f'Created {len(tenders)} tenders')
        return tenders

    def create_tender_documents(self, tenders):
        """Create tender documents"""
        self.stdout.write('Creating tender documents...')
        
        doc_count = 0
        doc_types = [
            ('tender_notice', 'Tender Notice Document'),
            ('technical_specs', 'Technical Specifications'),
            ('bill_quantities', 'Bill of Quantities'),
            ('terms_conditions', 'Terms and Conditions'),
        ]
        
        for tender in tenders:
            for doc_type, title in doc_types:
                TenderDocument.objects.get_or_create(
                    tender=tender,
                    document_type=doc_type,
                    defaults={
                        'title': f"{title} - {tender.tender_number}",
                        'file': f"tender_documents/{tender.tender_number}_{doc_type}.pdf",
                        'file_size': random.randint(500000, 5000000),
                        'description': f"{title} for {tender.title}",
                        'is_mandatory': True,
                    }
                )
                doc_count += 1

        self.stdout.write(f'Created {doc_count} tender documents')

    def create_amendments(self, tenders):
        """Create tender amendments"""
        self.stdout.write('Creating amendments...')
        
        amendments = []
        for tender in random.sample(tenders, min(4, len(tenders))):
            amendment, created = TenderAmendment.objects.get_or_create(
                tender=tender,
                amendment_number='AMD-001',
                defaults={
                    'title': 'Extension of Submission Deadline',
                    'description': 'The submission deadline has been extended by 14 days due to requests from prospective bidders.',
                    'affects_submission_deadline': True,
                    'new_submission_deadline': tender.submission_deadline + timedelta(days=14),
                    'published_at': tender.publication_date + timedelta(days=10),
                }
            )
            if created:
                amendments.append(amendment)

        self.stdout.write(f'Created {len(amendments)} amendments')

    def create_bids(self, tenders, vendors):
        """Create bids"""
        self.stdout.write('Creating bids...')
        
        bids = []
        bid_count = 1
        
        # Only create bids for published, ongoing, closed, or awarded tenders
        eligible_tenders = [t for t in tenders if t.status in ['published', 'ongoing', 'closed', 'awarded']]
        
        for tender in eligible_tenders:
            # 3-5 bids per tender
            num_bids = random.randint(3, min(5, len(vendors)))
            selected_vendors = random.sample(vendors, num_bids)
            
            for vendor in selected_vendors:
                # Bid amount variation around estimated value
                variation = random.uniform(0.85, 1.15)
                bid_amount = float(tender.estimated_value) * variation
                
                # Determine bid status based on tender status
                if tender.status == 'awarded':
                    status = random.choice(['rejected', 'shortlisted', 'awarded'])
                elif tender.status == 'closed':
                    status = random.choice(['submitted', 'under_review', 'shortlisted'])
                else:
                    status = random.choice(['submitted', 'under_review'])
                
                submitted_date = tender.publication_date + timedelta(
                    days=random.randint(5, (tender.submission_deadline - tender.publication_date).days)
                )
                
                bid, created = Bid.objects.get_or_create(
                    tender=tender,
                    vendor=vendor,
                    defaults={
                        'bid_number': f"BID-{tender.tender_number}-{bid_count:03d}",
                        'bid_amount': Decimal(str(round(bid_amount, 2))),
                        'currency': tender.currency,
                        'technical_proposal': f"Technical proposal for {tender.title} by {vendor.company_name}. We propose to execute this project using our experienced team and modern equipment.",
                        'financial_proposal': f"Financial breakdown: Materials 40%, Labor 30%, Equipment 20%, Overhead 10%",
                        'delivery_timeline_days': random.randint(
                            int(tender.contract_duration_days * 0.8),
                            tender.contract_duration_days
                        ),
                        'bid_security_reference': f"BS-{tender.tender_number}-{vendor.registration_number}",
                        'bid_security_amount': tender.bid_security_amount,
                        'status': status,
                        'technical_score': Decimal(str(random.randint(70, 98))) if status != 'draft' else None,
                        'financial_score': Decimal(str(random.randint(65, 95))) if status != 'draft' else None,
                        'total_score': Decimal(str(random.randint(70, 95))) if status != 'draft' else None,
                        'submitted_at': submitted_date if status != 'draft' else None,
                    }
                )
                if created:
                    bids.append(bid)
                    bid_count += 1

        self.stdout.write(f'Created {len(bids)} bids')
        return bids

    def create_bid_documents(self, bids):
        """Create bid documents"""
        self.stdout.write('Creating bid documents...')
        
        doc_count = 0
        doc_types = [
            ('technical_proposal', 'Technical Proposal'),
            ('financial_proposal', 'Financial Proposal'),
            ('company_profile', 'Company Profile'),
            ('registration_cert', 'Registration Certificate'),
            ('tax_clearance', 'Tax Clearance Certificate'),
        ]
        
        for bid in bids:
            for doc_type, title in doc_types:
                BidDocument.objects.get_or_create(
                    bid=bid,
                    document_type=doc_type,
                    defaults={
                        'title': f"{title} - {bid.vendor.company_name}",
                        'file': f"bid_documents/{bid.bid_number}_{doc_type}.pdf",
                        'description': f"{title} submitted by {bid.vendor.company_name}",
                    }
                )
                doc_count += 1

        self.stdout.write(f'Created {doc_count} bid documents')

    def create_clarifications(self, tenders, vendors):
        """Create clarifications"""
        self.stdout.write('Creating clarifications...')
        
        clarifications = []
        questions = [
            "What are the specific technical requirements for the equipment?",
            "Can foreign companies participate in consortium with local firms?",
            "Is there a site visit scheduled before bid submission?",
            "What is the payment schedule for this contract?",
            "Are there any ongoing projects that might affect the timeline?",
            "Can you provide more details about the evaluation criteria?",
            "Is pre-qualification mandatory for all bidders?",
            "What are the insurance requirements for this project?",
        ]
        
        answers = [
            "Please refer to Section 3.2 of the technical specifications document.",
            "Yes, joint ventures between foreign and local firms are acceptable as per tender conditions.",
            "A mandatory site visit is scheduled for next week. Details will be emailed to registered bidders.",
            "Payment will be made in milestones as outlined in the contract terms.",
            "No ongoing projects will affect the implementation timeline.",
            "Evaluation will be 70% technical and 30% financial as stated in the tender notice.",
            "Pre-qualification is only required for tenders exceeding KES 1 billion.",
            "Contractors must maintain comprehensive insurance as per Section 4.5 of the contract.",
        ]
        
        published_tenders = [t for t in tenders if t.status in ['published', 'ongoing']]
        
        for tender in random.sample(published_tenders, min(5, len(published_tenders))):
            num_clarifications = random.randint(2, 4)
            for i in range(num_clarifications):
                vendor = random.choice(vendors)
                is_answered = random.choice([True, True, False])
                
                asked_date = tender.publication_date + timedelta(days=random.randint(3, 15))
                answered_date = asked_date + timedelta(days=random.randint(1, 3)) if is_answered else None
                
                clarification = Clarification.objects.create(
                    tender=tender,
                    vendor=vendor,
                    question=random.choice(questions),
                    answer=random.choice(answers) if is_answered else '',
                    is_public=True,
                    is_answered=is_answered,
                    asked_at=asked_date,
                    answered_at=answered_date,
                )
                clarifications.append(clarification)

        self.stdout.write(f'Created {len(clarifications)} clarifications')

    def create_evaluations(self, tenders, users):
        """Create evaluations"""
        self.stdout.write('Creating evaluations...')
        
        evaluations = []
        eligible_tenders = [t for t in tenders if t.status in ['closed', 'awarded']]
        
        for tender in eligible_tenders:
            evaluation, created = Evaluation.objects.get_or_create(
                tender=tender,
                defaults={
                    'evaluator': random.choice(users[:4]),
                    'technical_criteria': {
                        'experience': {'weight': 20, 'description': 'Relevant experience and past projects'},
                        'methodology': {'weight': 25, 'description': 'Proposed methodology and approach'},
                        'team': {'weight': 15, 'description': 'Qualification of key personnel'},
                        'equipment': {'weight': 10, 'description': 'Equipment and resources'},
                    },
                    'financial_criteria': {
                        'price': {'weight': 30, 'description': 'Bid price competitiveness'},
                    },
                    'notes': 'Evaluation conducted as per procurement guidelines',
                    'is_completed': tender.status == 'awarded',
                }
            )
            if created:
                evaluations.append(evaluation)

        self.stdout.write(f'Created {len(evaluations)} evaluations')
        return evaluations

    def create_bid_evaluations(self, evaluations, bids):
        """Create bid evaluations"""
        self.stdout.write('Creating bid evaluations...')
        
        bid_evals = []
        
        for evaluation in evaluations:
            tender_bids = [b for b in bids if b.tender == evaluation.tender]
            
            for bid in tender_bids:
                tech_scores = {
                    'experience': random.randint(15, 20),
                    'methodology': random.randint(18, 25),
                    'team': random.randint(10, 15),
                    'equipment': random.randint(7, 10),
                }
                tech_total = sum(tech_scores.values())
                financial_score = random.randint(20, 30)
                total = tech_total + financial_score
                
                recommendation = 'recommend' if total >= 80 else 'conditional' if total >= 70 else 'not_recommend'
                
                bid_eval, created = BidEvaluation.objects.get_or_create(
                    evaluation=evaluation,
                    bid=bid,
                    defaults={
                        'technical_scores': tech_scores,
                        'financial_score': Decimal(str(financial_score)),
                        'total_score': Decimal(str(total)),
                        'remarks': f"Bid evaluated based on technical and financial criteria. Total score: {total}/100",
                        'recommendation': recommendation,
                    }
                )
                if created:
                    bid_evals.append(bid_eval)

        self.stdout.write(f'Created {len(bid_evals)} bid evaluations')

    def create_contracts(self, tenders, bids, vendors):
        """Create contracts"""
        self.stdout.write('Creating contracts...')
        
        contracts = []
        awarded_tenders = [t for t in tenders if t.status == 'awarded']
        contract_num = 1
        
        for tender in awarded_tenders:
            tender_bids = [b for b in bids if b.tender == tender and b.status == 'awarded']
            if not tender_bids:
                # Award to a random bid for this tender
                tender_bids = [b for b in bids if b.tender == tender]
                if tender_bids:
                    winning_bid = random.choice(tender_bids)
                    winning_bid.status = 'awarded'
                    winning_bid.save()
                else:
                    continue
            else:
                winning_bid = tender_bids[0]
            
            start_date = tender.opening_date.date() + timedelta(days=30)
            end_date = start_date + timedelta(days=tender.contract_duration_days)
            
            contract, created = Contract.objects.get_or_create(
                tender=tender,
                defaults={
                    'contract_number': f"CNT-2025-{contract_num:04d}",
                    'winning_bid': winning_bid,
                    'vendor': winning_bid.vendor,
                    'contract_value': winning_bid.bid_amount,
                    'currency': winning_bid.currency,
                    'start_date': start_date,
                    'end_date': end_date,
                    'duration_days': tender.contract_duration_days,
                    'status': random.choice(['active', 'active', 'completed']),
                    'terms_and_conditions': 'Standard government contract terms apply. Performance bond required. Monthly progress reports mandatory.',
                    'performance_bond_amount': winning_bid.bid_amount * Decimal('0.10'),
                    'retention_percentage': Decimal('10.0'),
                    'signed_by_organization': True,
                    'signed_by_vendor': True,
                }
            )
            if created:
                contracts.append(contract)
                contract_num += 1

        self.stdout.write(f'Created {len(contracts)} contracts')
        return contracts

    def create_milestones(self, contracts):
        """Create contract milestones"""
        self.stdout.write('Creating milestones...')
        
        milestones = []
        
        for contract in contracts:
            num_milestones = random.randint(3, 6)
            milestone_value = contract.contract_value / num_milestones
            
            for i in range(1, num_milestones + 1):
                days_offset = (contract.duration_days // num_milestones) * i
                due_date = contract.start_date + timedelta(days=days_offset)
                
                # Determine milestone status based on contract status and dates
                if contract.status == 'completed':
                    status = random.choice(['completed', 'verified', 'paid'])
                    completion_date = due_date - timedelta(days=random.randint(0, 5))
                    payment_date = completion_date + timedelta(days=random.randint(7, 14))
                elif contract.status == 'active' and due_date < timezone.now().date():
                    status = random.choice(['completed', 'in_progress', 'verified'])
                    completion_date = due_date if status != 'in_progress' else None
                    payment_date = None
                else:
                    status = 'pending'
                    completion_date = None
                    payment_date = None
                
                milestone = Milestone.objects.create(
                    contract=contract,
                    title=f"Milestone {i} - {self.get_milestone_title(i, num_milestones)}",
                    description=f"Deliverables for milestone {i} of {num_milestones}",
                    sequence_number=i,
                    deliverables=self.get_milestone_deliverables(i),
                    amount=milestone_value,
                    percentage_of_total=Decimal(str(round(100 / num_milestones, 2))),
                    due_date=due_date,
                    completion_date=completion_date,
                    payment_date=payment_date if status == 'paid' else None,
                    status=status,
                )
                milestones.append(milestone)

        self.stdout.write(f'Created {len(milestones)} milestones')
        return milestones

    def get_milestone_title(self, num, total):
        """Get milestone title based on sequence"""
        titles = {
            1: "Project Mobilization and Site Preparation",
            2: "Foundation and Structural Work",
            3: "Main Construction Phase",
            4: "Finishing and Installation",
            5: "Testing and Commissioning",
            6: "Final Handover and Documentation",
        }
        return titles.get(num, f"Phase {num}")

    def get_milestone_deliverables(self, num):
        """Get milestone deliverables"""
        deliverables = {
            1: "Site mobilization, temporary facilities, material procurement, approved drawings",
            2: "Completed foundation work, structural framework, inspection certificates",
            3: "Main construction completed, MEP rough-in, progress photos",
            4: "Finishing work, equipment installation, training materials",
            5: "System testing reports, commissioning certificates, user training",
            6: "As-built drawings, operation manuals, warranty documents, final inspection",
        }
        return deliverables.get(num, "Project deliverables as per contract")

    def create_reviews(self, contracts, users):
        """Create reviews for completed contracts"""
        self.stdout.write('Creating reviews...')
        
        reviews = []
        completed_contracts = [c for c in contracts if c.status == 'completed']
        
        for contract in completed_contracts:
            if random.random() > 0.3:  # 70% chance of review
                quality = random.randint(3, 5)
                timeliness = random.randint(3, 5)
                professionalism = random.randint(3, 5)
                overall = (quality + timeliness + professionalism) / 3
                
                review, created = Review.objects.get_or_create(
                    contract=contract,
                    defaults={
                        'reviewer': random.choice(users[:4]),
                        'quality_rating': quality,
                        'timeliness_rating': timeliness,
                        'professionalism_rating': professionalism,
                        'overall_rating': Decimal(str(round(overall, 2))),
                        'comment': self.get_review_comment(overall),
                        'would_work_again': overall >= 3.5,
                    }
                )
                if created:
                    reviews.append(review)

        self.stdout.write(f'Created {len(reviews)} reviews')
        return reviews

    def get_review_comment(self, rating):
        """Get review comment based on rating"""
        if rating >= 4.5:
            return "Excellent performance. Project delivered on time with high quality standards. Highly professional team. Would definitely work with this vendor again."
        elif rating >= 4.0:
            return "Very good performance. Minor delays but overall satisfactory delivery. Good communication throughout the project."
        elif rating >= 3.5:
            return "Satisfactory performance. Project completed as per requirements. Some areas could be improved for future engagements."
        else:
            return "Performance was below expectations. Several issues encountered during project execution. Improvements needed in project management."

    def create_notifications(self, users):
        """Create sample notifications"""
        self.stdout.write('Creating notifications...')
        
        notifications = []
        notification_templates = [
            ('tender_published', 'New Tender Published', 'A new tender matching your interests has been published.'),
            ('tender_closing', 'Tender Closing Soon', 'Reminder: Tender submission deadline is approaching in 3 days.'),
            ('bid_submitted', 'Bid Submitted Successfully', 'Your bid has been submitted successfully.'),
            ('bid_status_change', 'Bid Status Updated', 'Your bid status has been updated to: Under Review'),
            ('clarification_answered', 'Clarification Answered', 'Your clarification question has been answered.'),
            ('amendment_published', 'Tender Amendment', 'An amendment has been published for a tender you are tracking.'),
            ('milestone_due', 'Milestone Due Soon', 'Project milestone is due in 5 days. Please ensure timely delivery.'),
        ]
        
        vendor_users = [u for u in users if u.username.startswith('vendor')]
        
        for user in vendor_users:
            # Create 3-7 notifications per vendor user
            num_notifications = random.randint(3, 7)
            for _ in range(num_notifications):
                notif_type, title, message = random.choice(notification_templates)
                is_read = random.choice([True, True, False])  # 66% chance of being read
                
                created_date = timezone.now() - timedelta(days=random.randint(1, 30))
                read_date = created_date + timedelta(hours=random.randint(1, 48)) if is_read else None
                
                notification = Notification.objects.create(
                    recipient=user,
                    notification_type=notif_type,
                    title=title,
                    message=message,
                    link=f"/tenders/{random.randint(1, 100)}/",
                    is_read=is_read,
                    created_at=created_date,
                    read_at=read_date,
                )
                notifications.append(notification)

        self.stdout.write(f'Created {len(notifications)} notifications')
        return notifications