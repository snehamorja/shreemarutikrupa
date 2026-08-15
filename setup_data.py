import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scaife_project.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import (
    BrandingSettings, Office, UserProfile, PricingConfig, 
    ScaifeEntry, Inquiry, FAQ, Testimonial, GalleryItem, ActivityLog
)
from django.utils import timezone
import datetime

def populate_database():
    print("Populating initial data...")

    # 1. Branding Settings
    branding = BrandingSettings.get_solo()
    branding.company_name = "Apex Scaife Lapping & Coating"
    branding.tagline = "Premium Industrial Solutions for High-Precision Diamond Processing"
    branding.contact_email = "info@apexscaife.com"
    branding.contact_phone = "+91 98765 43210"
    branding.address = "Sector 4, Diamond GIDC Industrial Area, Ichhapore, Surat, Gujarat, India"
    branding.office_hours = "Monday to Saturday: 8:30 AM - 7:00 PM"
    branding.whatsapp_number = "+91 98765 43210"
    branding.save()
    print("Branding Settings configured.")

    # 2. Pricing Configuration
    pricing = PricingConfig.get_solo()
    pricing.lapping_rate = 150.00
    pricing.coating_rate = 200.00
    pricing.save()
    print("Pricing Configuration initialized.")

    # 3. Create Offices
    surat_office, _ = Office.objects.get_or_create(
        name="Surat Industrial Hub (HQ)",
        location="GIDC Ichhapore, Surat, Gujarat, 394510",
        phone="+91 98765 43210",
        email="surat@apexscaife.com"
    )
    mumbai_office, _ = Office.objects.get_or_create(
        name="Mumbai Service Center",
        location="Kurla Industrial Estate, Ghatkopar, Mumbai, 400086",
        phone="+91 98765 43215",
        email="mumbai@apexscaife.com"
    )
    print("Offices created.")

    # 4. Create Users and Profiles
    # Admin User
    if not User.objects.filter(username="admin").exists():
        admin_user = User.objects.create_superuser(
            username="admin", 
            email="admin@apexscaife.com", 
            password="adminpassword123"
        )
        admin_user.first_name = "Super"
        admin_user.last_name = "Admin"
        admin_user.save()
        
        # Profile is created automatically by signal, update role
        profile = admin_user.profile
        profile.role = 'admin'
        profile.save()
        print("Admin user created (User: admin, Pass: adminpassword123)")
    else:
        admin_user = User.objects.get(username="admin")

    # Office Manager User (Surat)
    if not User.objects.filter(username="manager").exists():
        manager_user = User.objects.create_user(
            username="manager", 
            email="manager@apexscaife.com", 
            password="managerpassword123"
        )
        manager_user.first_name = "Rajesh"
        manager_user.last_name = "Patel"
        manager_user.save()
        
        profile = manager_user.profile
        profile.role = 'manager'
        profile.office = surat_office
        profile.save()
        print("Manager user created (User: manager, Pass: managerpassword123)")
    else:
        manager_user = User.objects.get(username="manager")

    # Office Worker User (Mumbai)
    if not User.objects.filter(username="worker").exists():
        worker_user = User.objects.create_user(
            username="worker", 
            email="worker@apexscaife.com", 
            password="workerpassword123"
        )
        worker_user.first_name = "Amit"
        worker_user.last_name = "Shah"
        worker_user.save()
        
        profile = worker_user.profile
        profile.role = 'worker'
        profile.office = mumbai_office
        profile.save()
        print("Worker user created (User: worker, Pass: workerpassword123)")

    # 5. Populate FAQs
    FAQs_data = [
        ("What is Diamond Scaife Lapping?", "Scaife lapping is a high-precision process of grinding the surface of a diamond scaife (the cast iron wheel used for diamond cutting) to make it perfectly flat, clean, and balanced. This enables diamonds to be cut and polished smoothly without micro-fracturing.", 1),
        ("Why does a scaife require specialized coating?", "Coating provides a durable, micro-porous layer that holds diamond dust (the abrasive media) securely onto the wheel. Specialized coatings like Premium Diamond-Like Carbon (DLC) prolong the life of the scaife, optimize abrasive utilization, and ensure faster and cleaner cuts.", 2),
        ("How often does a scaife need maintenance?", "Depending on production volume, a scaife needs lapping and coating every 40 to 60 hours of continuous operations. Regular inspection prevents uneven wear and ensures consistent polish quality.", 3),
        ("What parameters affect lapping and coating costs?", "Cost is calculated primarily based on the outer diameter of the scaife (charged per inch) and the specific type of lapping (Standard, Precision, Ultra-Precision) and coating (Standard, Premium, DLC) chosen.", 4),
        ("Can we track our scaife processing status?", "Yes! Through our online portal, office staff can update progress and clients can request status. You will also receive an email notification when processing completes.", 5),
    ]

    for q, a, order in FAQs_data:
        FAQ.objects.get_or_create(
            question=q,
            defaults={'answer': a, 'display_order': order, 'is_active': True}
        )
    print("FAQs populated.")

    # 6. Testimonials
    testimonials_data = [
        ("Mahendra Mehta", "Mehta Diamonds Ltd.", "The DLC coating on our scaifes lasted twice as long as traditional coatings. Our diamond cutters report exceptionally smooth polishing action.", 5),
        ("Ketan Savani", "Savani & Sons Polishing", "Apex Scaife's precision lapping services restored our warped scaife plates to sub-micron flatness. Their turnaround time is outstanding.", 5),
        ("Harish Choksi", "Choksi Exports", "We have been routing all our scaife maintenance through Mumbai and Surat offices for 5 years. Highly recommended for professionalism and reliability.", 4),
    ]

    for name, company, review, rating in testimonials_data:
        Testimonial.objects.get_or_create(
            client_name=name,
            company=company,
            defaults={'review_text': review, 'rating': rating, 'is_active': True}
        )
    print("Testimonials populated.")

    # 7. Sample Scaife Entries
    scaife_data = [
        ("Kiran Gem Corp",          3, True,  True,  False, surat_office,  manager_user),
        ("Hari Krishna Exports",     2, True,  True,  False, surat_office,  manager_user),
        ("Dharmanandan Diamonds",    1, True,  False, True,  mumbai_office, manager_user),
        ("Venus Jewel",              5, True,  False, False, surat_office,  manager_user),
        ("Shree Ramkrishna Export",  2, False, True,  False, mumbai_office, manager_user),
    ]

    for client, qty, lap, coat, diamond, office, creator in scaife_data:
        if not ScaifeEntry.objects.filter(client_name=client, quantity=qty).exists():
            entry = ScaifeEntry(
                client_name=client,
                quantity=qty,
                service_lapping=lap,
                service_coating=coat,
                service_diamond_scaife=diamond,
                status='received',
                assigned_office=office,
                created_by=creator,
                notes=f"Sample record for {client} processing."
            )
            entry.save()
    print("Sample Scaife entries populated.")

    # 8. Sample Inquiries
    inquiries_data = [
        ("Nilesh Kheni", "nilesh@khenidiamonds.com", "+91 99887 76655", "DLC Coating Inquiry", "We have a batch of 8 scaifes that need Diamond-Like Carbon coating. Can you provide a bulk discount estimation?", "new"),
        ("Sanjay Vaghani", "sanjay@vaghanigems.in", "+91 98989 89898", "Lapping machine issue", "Our own team is experiencing issues with our in-house lapping plate. Do you offer on-site consultation services?", "contacted"),
    ]

    for name, email, phone, subject, msg, status in inquiries_data:
        Inquiry.objects.get_or_create(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            defaults={'message': msg, 'status': status}
        )
    print("Sample Inquiries populated.")



    print("\nDatabase initialization complete! You can log in with:")
    print("Admin: admin / adminpassword123")
    print("Manager: manager / managerpassword123")
    print("Worker: worker / workerpassword123")

if __name__ == "__main__":
    populate_database()
