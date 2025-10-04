from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import MinValueValidator, FileExtensionValidator
from decimal import Decimal
import uuid


class Organization(models.Model):
    """Organizations that post tenders"""
    ORG_TYPES = [
        ('government', 'Government'),
        ('private', 'Private Company'),
        ('construction', 'Construction Company'),
        ('military', 'Military/Defense'),
        ('education', 'Educational Institution'),
        ('healthcare', 'Healthcare'),
        ('ngo', 'NGO/Non-Profit'),
        ('parastatal', 'Parastatal'),
        ('municipality', 'Municipality'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    organization_type = models.CharField(max_length=50, choices=ORG_TYPES)
    registration_number = models.CharField(max_length=100, unique=True)
    tax_id = models.CharField(max_length=100, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    website = models.URLField(blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='organizations/logos/', blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']


class TenderCategory(models.Model):
    """Categories for different types of tenders"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # For icon class names
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Tender Categories"
        ordering = ['name']


class Tender(models.Model):
    """Main Tender Model"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('ongoing', 'Ongoing'),
        ('closed', 'Closed'),
        ('awarded', 'Awarded'),
        ('cancelled', 'Cancelled'),
    ]
    
    PROCUREMENT_METHODS = [
        ('open', 'Open Tender'),
        ('restricted', 'Restricted Tender'),
        ('negotiated', 'Negotiated Procedure'),
        ('framework', 'Framework Agreement'),
        ('competitive_dialogue', 'Competitive Dialogue'),
        ('request_quotation', 'Request for Quotation'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tender_number = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    title = models.CharField(max_length=500)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='tenders')
    category = models.ForeignKey(TenderCategory, on_delete=models.SET_NULL, null=True, related_name='tenders')
    
    description = models.TextField()
    detailed_requirements = models.TextField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    procurement_method = models.CharField(max_length=50, choices=PROCUREMENT_METHODS)
    
    # Financial
    estimated_value = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    currency = models.CharField(max_length=3, default='USD')
    bid_security_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Dates
    publication_date = models.DateTimeField()
    submission_deadline = models.DateTimeField()
    opening_date = models.DateTimeField()
    expected_award_date = models.DateField(null=True, blank=True)
    contract_duration_days = models.PositiveIntegerField(null=True, blank=True)
    
    # Location
    project_location = models.CharField(max_length=255)
    project_city = models.CharField(max_length=100)
    project_country = models.CharField(max_length=100)
    
    # Eligibility
    eligible_countries = models.TextField(help_text="Comma-separated country codes")
    minimum_experience_years = models.PositiveIntegerField(default=0)
    minimum_turnover = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    requires_prequalification = models.BooleanField(default=False)
    
    # Contact
    contact_person = models.CharField(max_length=255)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    
    # Metadata
    views_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_tenders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            self.slug = f"{base_slug}-{self.tender_number.lower()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.tender_number} - {self.title}"
    
    class Meta:
        ordering = ['-publication_date']
        indexes = [
            models.Index(fields=['status', 'submission_deadline']),
            models.Index(fields=['category', 'status']),
        ]


class TenderDocument(models.Model):
    """Documents attached to tenders"""
    DOC_TYPES = [
        ('tender_notice', 'Tender Notice'),
        ('technical_specs', 'Technical Specifications'),
        ('bill_quantities', 'Bill of Quantities'),
        ('drawings', 'Drawings/Plans'),
        ('terms_conditions', 'Terms and Conditions'),
        ('contract_template', 'Contract Template'),
        ('prequalification', 'Prequalification Document'),
        ('addendum', 'Addendum'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=50, choices=DOC_TYPES)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, blank=True)
    file = models.FileField(upload_to='tender_documents/')
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    description = models.TextField(blank=True)
    is_mandatory = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.id}")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.tender.tender_number} - {self.title}"
    
    class Meta:
        ordering = ['document_type', 'title']


class Vendor(models.Model):
    """Companies/Vendors that bid on tenders"""
    BUSINESS_TYPES = [
        ('sole_proprietor', 'Sole Proprietorship'),
        ('partnership', 'Partnership'),
        ('llc', 'Limited Liability Company'),
        ('corporation', 'Corporation'),
        ('cooperative', 'Cooperative'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    business_type = models.CharField(max_length=50, choices=BUSINESS_TYPES)
    registration_number = models.CharField(max_length=100, unique=True)
    tax_id = models.CharField(max_length=100)
    
    # Contact
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    website = models.URLField(blank=True)
    
    # Address
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    
    # Business Info
    year_established = models.PositiveIntegerField()
    number_of_employees = models.PositiveIntegerField()
    annual_turnover = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Capabilities
    categories = models.ManyToManyField(TenderCategory, related_name='vendors')
    service_areas = models.TextField(help_text="Countries/regions where vendor operates")
    
    # Verification
    is_verified = models.BooleanField(default=False)
    is_blacklisted = models.BooleanField(default=False)
    verification_documents = models.FileField(upload_to='vendor_documents/', blank=True)
    
    # Ratings
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_reviews = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.company_name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.company_name
    
    class Meta:
        ordering = ['-created_at']


class Bid(models.Model):
    """Bids submitted by vendors for tenders"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('awarded', 'Awarded'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bid_number = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name='bids')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='bids')
    
    # Bid Details
    bid_amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    currency = models.CharField(max_length=3, default='USD')
    
    technical_proposal = models.TextField()
    financial_proposal = models.TextField()
    delivery_timeline_days = models.PositiveIntegerField()
    
    # Security
    bid_security_reference = models.CharField(max_length=100, blank=True)
    bid_security_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Evaluation
    technical_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    financial_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    total_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    evaluator_comments = models.TextField(blank=True)
    
    # Timestamps
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.vendor.company_name}-{self.tender.tender_number}-{self.bid_number}")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.bid_number} - {self.vendor.company_name}"
    
    class Meta:
        ordering = ['-submitted_at']
        unique_together = ['tender', 'vendor']


class BidDocument(models.Model):
    """Documents submitted with bids"""
    DOC_TYPES = [
        ('technical_proposal', 'Technical Proposal'),
        ('financial_proposal', 'Financial Proposal'),
        ('company_profile', 'Company Profile'),
        ('registration_cert', 'Registration Certificate'),
        ('tax_clearance', 'Tax Clearance'),
        ('financial_statements', 'Financial Statements'),
        ('experience_cert', 'Experience Certificates'),
        ('bid_security', 'Bid Security'),
        ('power_attorney', 'Power of Attorney'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=50, choices=DOC_TYPES)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, blank=True)
    file = models.FileField(upload_to='bid_documents/')
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.id}")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.bid.bid_number} - {self.title}"


class TenderAmendment(models.Model):
    """Amendments/Addendums to tenders"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name='amendments')
    amendment_number = models.CharField(max_length=50)
    slug = models.SlugField(max_length=300, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    affects_submission_deadline = models.BooleanField(default=False)
    new_submission_deadline = models.DateTimeField(null=True, blank=True)
    affects_estimated_value = models.BooleanField(default=False)
    new_estimated_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    document = models.FileField(upload_to='amendments/', blank=True)
    published_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.tender.tender_number}-{self.amendment_number}")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.tender.tender_number} - Amendment {self.amendment_number}"
    
    class Meta:
        ordering = ['-published_at']


class Clarification(models.Model):
    """Questions and clarifications about tenders"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name='clarifications')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='clarifications')
    question = models.TextField()
    answer = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)
    is_answered = models.BooleanField(default=False)
    asked_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.tender.tender_number} - Clarification"
    
    class Meta:
        ordering = ['-asked_at']


class Contract(models.Model):
    """Contracts awarded from tenders"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('completed', 'Completed'),
        ('terminated', 'Terminated'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract_number = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    tender = models.OneToOneField(Tender, on_delete=models.CASCADE, related_name='contract')
    winning_bid = models.OneToOneField(Bid, on_delete=models.CASCADE, related_name='contract')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='contracts')
    
    contract_value = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    start_date = models.DateField()
    end_date = models.DateField()
    duration_days = models.PositiveIntegerField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    terms_and_conditions = models.TextField()
    performance_bond_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    retention_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.0)
    
    signed_contract = models.FileField(upload_to='contracts/', blank=True)
    signed_by_organization = models.BooleanField(default=False)
    signed_by_vendor = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.contract_number}-{self.vendor.company_name}")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.contract_number} - {self.vendor.company_name}"
    
    class Meta:
        ordering = ['-created_at']


class Milestone(models.Model):
    """Contract milestones and payments"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('verified', 'Verified'),
        ('paid', 'Paid'),
        ('delayed', 'Delayed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, blank=True)
    description = models.TextField()
    
    sequence_number = models.PositiveIntegerField()
    deliverables = models.TextField()
    
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    percentage_of_total = models.DecimalField(max_digits=5, decimal_places=2)
    
    due_date = models.DateField()
    completion_date = models.DateField(null=True, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    verification_document = models.FileField(upload_to='milestone_verifications/', blank=True)
    payment_receipt = models.FileField(upload_to='payment_receipts/', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.contract.contract_number}-milestone-{self.sequence_number}")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.contract.contract_number} - Milestone {self.sequence_number}"
    
    class Meta:
        ordering = ['contract', 'sequence_number']
        unique_together = ['contract', 'sequence_number']


class Evaluation(models.Model):
    """Tender evaluation records"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name='evaluations')
    evaluator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    evaluation_date = models.DateTimeField(auto_now_add=True)
    
    technical_criteria = models.JSONField()  # Store evaluation criteria and weights
    financial_criteria = models.JSONField()
    
    notes = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Evaluation - {self.tender.tender_number}"
    
    class Meta:
        ordering = ['-evaluation_date']


class BidEvaluation(models.Model):
    """Individual bid evaluation scores"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name='bid_evaluations')
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE, related_name='evaluations')
    
    technical_scores = models.JSONField()  # Detailed scoring breakdown
    financial_score = models.DecimalField(max_digits=5, decimal_places=2)
    total_score = models.DecimalField(max_digits=5, decimal_places=2)
    
    remarks = models.TextField(blank=True)
    recommendation = models.CharField(max_length=50, choices=[
        ('recommend', 'Recommend'),
        ('conditional', 'Conditional'),
        ('not_recommend', 'Not Recommended'),
    ])
    
    evaluated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.bid.bid_number} - Score: {self.total_score}"
    
    class Meta:
        ordering = ['-total_score']
        unique_together = ['evaluation', 'bid']


class Notification(models.Model):
    """Notifications for users"""
    NOTIFICATION_TYPES = [
        ('tender_published', 'Tender Published'),
        ('tender_closing', 'Tender Closing Soon'),
        ('bid_submitted', 'Bid Submitted'),
        ('bid_status_change', 'Bid Status Changed'),
        ('clarification_answered', 'Clarification Answered'),
        ('amendment_published', 'Amendment Published'),
        ('contract_awarded', 'Contract Awarded'),
        ('milestone_due', 'Milestone Due'),
        ('payment_released', 'Payment Released'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True)
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.recipient.username} - {self.title}"
    
    class Meta:
        ordering = ['-created_at']


class Review(models.Model):
    """Reviews and ratings for completed contracts"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract = models.OneToOneField(Contract, on_delete=models.CASCADE, related_name='review')
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    quality_rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    timeliness_rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    professionalism_rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    overall_rating = models.DecimalField(max_digits=3, decimal_places=2)
    
    comment = models.TextField()
    would_work_again = models.BooleanField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Review - {self.contract.contract_number}"
    
    class Meta:
        ordering = ['-created_at']