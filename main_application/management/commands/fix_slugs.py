from django.core.management.base import BaseCommand
from main_application.models import Tender

class Command(BaseCommand):
    help = "Fix tender slugs by replacing / with -"

    def handle(self, *args, **kwargs):
        tenders = Tender.objects.all()
        updated_count = 0

        for tender in tenders:
            if "/" in tender.slug:
                old_slug = tender.slug
                tender.slug = old_slug.replace("/", "-")
                tender.save(update_fields=["slug"])
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f"Updated slug: {old_slug} -> {tender.slug}"
                ))

        if updated_count == 0:
            self.stdout.write(self.style.WARNING("No slugs needed fixing."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Fixed {updated_count} slugs."))
