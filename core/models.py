from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import os
import shutil
import datetime
from pathlib import Path
from django.conf import settings

# 1. BrandingSettings (Singleton)
class BrandingSettings(models.Model):
    company_name = models.CharField(max_length=100, default="Scaife Tech Lapping & Coating")
    tagline = models.CharField(max_length=200, default="Precision Engineering for Diamond Scaifes")
    logo = models.ImageField(upload_to="branding/", null=True, blank=True)
    favicon = models.ImageField(upload_to="branding/", null=True, blank=True)
    banner = models.ImageField(upload_to="branding/", null=True, blank=True)
    
    # Contact info
    contact_email = models.EmailField(default="contact@scaifetech.com")
    contact_phone = models.CharField(max_length=20, default="+91 98765 43210")
    address = models.TextField(default="123 Diamond Industrial Estate, Surat, Gujarat, India")
    office_hours = models.CharField(max_length=100, default="Mon - Sat: 9:00 AM - 6:00 PM")
    whatsapp_number = models.CharField(max_length=20, default="+91 98765 43210")
    google_map_embed = models.TextField(
        blank=True, 
        null=True, 
        default="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3719.8276023737227!2d72.86311681493527!3d21.199014185908866!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3be04f21db5ab1c1%3A0x7d6a505e94b29bb8!2sVarachha%20Road%2C%20Surat%2C%20Gujarat%2C%20India!5e0!3m2!1sen!2sus!4v1620000000000!5m2!1sen!2sus"
    )
    footer_text = models.TextField(default="© 2026 Scaife Tech. All rights reserved. Premium lapping & coating solutions.")
    
    # Social Links
    facebook_url = models.URLField(blank=True, default="https://facebook.com")
    twitter_url = models.URLField(blank=True, default="https://twitter.com")
    linkedin_url = models.URLField(blank=True, default="https://linkedin.com")
    instagram_url = models.URLField(blank=True, default="https://instagram.com")
    
    # Master Security PIN to view office manager passwords
    admin_security_pin = models.CharField(max_length=20, default="1234", help_text="Master Security PIN required to reveal office manager passwords")

    def __str__(self):
        return self.company_name

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj


# 2. Office Model
class Office(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    manager_username = models.CharField(max_length=150, blank=True, default='', help_text="Auto-generated manager login username")
    manager_whatsapp = models.CharField(max_length=20, blank=True, default='', help_text="Manager's WhatsApp number (with country code, e.g. 919876543210)")

    def __str__(self):
        return self.name


# 2b. Office Credential & Password Change History
class OfficeCredentialHistory(models.Model):
    office = models.ForeignKey(Office, on_delete=models.CASCADE, related_name='credential_history')
    username = models.CharField(max_length=150)
    password_text = models.CharField(max_length=128, blank=True, help_text="Password recorded at change")
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    change_type = models.CharField(max_length=100, default="Password Changed")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.office.name} - {self.username} ({self.change_type})"



# 3. User Profile for Roles
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Super Admin'),
        ('manager', 'Office Manager'),
        ('worker', 'Office Worker'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='worker')
    office = models.ForeignKey(Office, on_delete=models.SET_NULL, null=True, blank=True, related_name='staff')

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.profile.save()


# 4. Pricing Configuration (Singleton for base prices)
class PricingConfig(models.Model):
    lapping_rate = models.DecimalField(max_digits=10, decimal_places=2, default=150.00, help_text="Lapping rate per scaife (INR)")
    coating_rate = models.DecimalField(max_digits=10, decimal_places=2, default=200.00, help_text="Coating rate per scaife (INR)")
    diamond_scaife_rate = models.DecimalField(max_digits=10, decimal_places=2, default=300.00, help_text="Diamond Scaife rate per scaife (INR)")

    def __str__(self):
        return "Pricing Configuration"

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj


# 5. Scaife Entry Model
class ScaifeEntry(models.Model):
    STATUS_CHOICES = [
        ('received', 'Received'),
        ('lapping', 'In Lapping'),
        ('coating', 'In Coating'),
        ('qc', 'Quality Control'),
        ('ready', 'Ready for Delivery'),
        ('delivered', 'Delivered'),
    ]

    client_name = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.IntegerField(default=1, help_text="Quantity of Scaifes")
    quantity_lapping = models.IntegerField(default=0, help_text="Quantity of Lapping Scaifes")
    quantity_coating = models.IntegerField(default=0, help_text="Quantity of Coating Scaifes")
    quantity_diamond = models.IntegerField(default=0, help_text="Quantity of Diamond Scaifes")
    diameter = models.DecimalField(max_digits=5, decimal_places=2, default=1.00, help_text="Plate Diameter in inches (legacy)")

    service_lapping = models.BooleanField(default=True)
    service_coating = models.BooleanField(default=False)
    service_diamond_scaife = models.BooleanField(default=False)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='received')
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    assigned_office = models.ForeignKey(Office, on_delete=models.CASCADE, related_name='scaife_entries', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_entries')
    
    received_date = models.DateField(auto_now_add=True)
    target_date = models.DateField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)
    
    # Repair Configuration
    needs_repair = models.BooleanField(default=False, help_text="Does this scaife require repair?")
    repair_details = models.TextField(blank=True, default='', help_text="Details of repair instructions (e.g. 'I have to repair this and that')")
    
    notes = models.TextField(blank=True)

    def calculate_cost(self):
        from decimal import Decimal
        pricing = PricingConfig.get_solo()
        total = Decimal('0.00')

        if self.service_lapping:
            q = Decimal(str(self.quantity_lapping if self.quantity_lapping > 0 else (self.quantity or 1)))
            total += q * Decimal(str(pricing.lapping_rate))

        if self.service_coating:
            q = Decimal(str(self.quantity_coating if self.quantity_coating > 0 else (self.quantity or 1)))
            total += q * Decimal(str(pricing.coating_rate))

        if self.service_diamond_scaife:
            q = Decimal(str(self.quantity_diamond if self.quantity_diamond > 0 else (self.quantity or 1)))
            total += q * Decimal(str(pricing.diamond_scaife_rate))

        return total

    def save(self, *args, **kwargs):
        from decimal import Decimal
        # Auto-set client_name from office if not provided
        if not self.client_name and self.assigned_office:
            self.client_name = self.assigned_office.name
        elif not self.client_name:
            self.client_name = 'Factory'

        # Auto-sum total quantity from per-service quantities
        lap = self.quantity_lapping if self.service_lapping else 0
        coat = self.quantity_coating if self.service_coating else 0
        dia = self.quantity_diamond if self.service_diamond_scaife else 0
        service_total = lap + coat + dia
        if service_total > 0:
            self.quantity = service_total
        elif not self.quantity:
            self.quantity = 1

        # Generate serial number if missing
        if not self.serial_number:
            import uuid
            self.serial_number = f"SCF-{uuid.uuid4().hex[:6].upper()}"

        # Always recalculate cost from current quantities and rates
        self.cost = self.calculate_cost()
        if not self.cost or self.cost == 0:
            self.cost = Decimal('0.00')

        super().save(*args, **kwargs)
        
        # Trigger automatic backup after save (at most once a day to prevent disk spam)
        try:
            self._run_auto_backup()
        except Exception:
            pass

    def _run_auto_backup(self):
        backup_dir = Path(settings.BASE_DIR) / 'backups'
        backup_dir.mkdir(exist_ok=True)
        
        today_str = datetime.datetime.now().strftime("%Y%m%d")
        today_backups = list(backup_dir.glob(f"backup_{today_str}_*.sqlite3"))
        
        if not today_backups:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_{timestamp}.sqlite3"
            backup_path = backup_dir / backup_filename
            src_path = Path(settings.BASE_DIR) / 'db.sqlite3'
            
            if src_path.exists():
                shutil.copy2(src_path, backup_path)
                
            # Retain last 7 days backups
            all_backups = sorted(list(backup_dir.glob("backup_*.sqlite3")))
            if len(all_backups) > 7:
                for old_backup in all_backups[:-7]:
                    try:
                        os.remove(old_backup)
                    except Exception:
                        pass

    def get_services_display(self):
        services = []
        if self.service_lapping:
            services.append("Lapping")
        if self.service_coating:
            services.append("Coating")
        if self.service_diamond_scaife:
            services.append("Diamond Scaife")
        return ", ".join(services) if services else "None"

    def __str__(self):
        return f"{self.client_name} - Qty: {self.quantity}"


# 6. Inquiry Model (Contact Form)
class Inquiry(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('resolved', 'Resolved'),
    ]
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"


# 7. FAQ Model
class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return self.question


# 8. GalleryItem Model
class GalleryItem(models.Model):
    CATEGORY_CHOICES = [
        ('office', 'Office & Infrastructure'),
        ('machine', 'Lapping & Coating Machinery'),
        ('process', 'Work Process'),
        ('product', 'Finished Scaifes'),
    ]
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="gallery/")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='process')
    display_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return self.title


# 9. TeamMember Model
class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    image = models.ImageField(upload_to="team/", null=True, blank=True)
    bio = models.TextField(blank=True)
    display_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return self.name


# 10. Testimonial Model
class Testimonial(models.Model):
    client_name = models.CharField(max_length=100)
    company = models.CharField(max_length=100, blank=True)
    review_text = models.TextField()
    rating = models.IntegerField(default=5)  # 1 to 5 stars
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.client_name} - {self.company}"


# 11. ActivityLog Model for Audit Trail
class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='logs')
    action_type = models.CharField(max_length=50)  # e.g., 'CREATE', 'UPDATE', 'DELETE', 'LOGIN', 'RESTORE'
    model_name = models.CharField(max_length=100, blank=True)
    object_repr = models.CharField(max_length=200, blank=True)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        user_str = self.user.username if self.user else "System"
        return f"{user_str} - {self.action_type} - {self.model_name} at {self.timestamp}"


# Helper function to create log entries
def log_action(user, action_type, model_name="", object_repr="", details=""):
    ActivityLog.objects.create(
        user=user if user and user.is_authenticated else None,
        action_type=action_type,
        model_name=model_name,
        object_repr=object_repr,
        details=details
    )


# ============================================================
# Worker Profile & Financial Ledger Models
# ============================================================
class WorkerProfile(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    office = models.ForeignKey(Office, on_delete=models.SET_NULL, null=True, blank=True, related_name='workers')
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='worker_profile')
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Base monthly/per-term salary in INR")
    joining_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.office.name if self.office else 'No Office'})"

    def _sum_entries(self, entry_type):
        from decimal import Decimal
        return sum((e.amount for e in self.financial_entries.filter(entry_type=entry_type)), Decimal('0.00'))

    def total_salary(self):
        from decimal import Decimal
        val = self._sum_entries('salary')
        return val if val else Decimal(str(self.base_salary))

    def total_advance(self):      return self._sum_entries('advance')
    def total_cash_taken(self):   return self._sum_entries('cash_taken')
    def total_bonus(self):        return self._sum_entries('bonus')
    def total_deductions(self):   return self._sum_entries('deduction')
    def total_expenses(self):     return self._sum_entries('expense')
    def total_income(self):       return self._sum_entries('income')
    def total_payments(self):     return self._sum_entries('payment')

    def total_leaves(self):
        return sum(e.leave_days for e in self.financial_entries.filter(entry_type='leave'))

    def pending_balance(self):
        earnings = self.total_salary() + self.total_bonus() + self.total_expenses() + self.total_income()
        paid_out = self.total_advance() + self.total_cash_taken() + self.total_deductions() + self.total_payments()
        return earnings - paid_out


class WorkerFinancialEntry(models.Model):
    ENTRY_TYPES = [
        ('salary',    '💰 Salary (પગાર)'),
        ('advance',   '💵 Advance (એડવાન્સ)'),
        ('cash_taken','🏦 Cash Taken (ઉપાડ)'),
        ('leave',     '📅 Leave (રજા)'),
        ('bonus',     '🎁 Bonus (બોનસ)'),
        ('deduction', '➖ Deduction (કપાત)'),
        ('expense',   '💸 Expense (ખર્ચ)'),
        ('income',    '📈 Income (આવક)'),
        ('payment',   '💳 Payment (ચુકવણી)'),
    ]

    worker     = models.ForeignKey(WorkerProfile, on_delete=models.CASCADE, related_name='financial_entries')
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPES)
    amount     = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    leave_days = models.IntegerField(default=0, help_text="Number of leave days (only for Leave type)")
    date       = models.DateField(default=timezone.now)
    notes      = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.worker.name} - {self.get_entry_type_display()} ({self.amount})"




