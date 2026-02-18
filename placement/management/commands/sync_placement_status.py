from django.core.management.base import BaseCommand
from placement.models import JobApplication, StudentProfile


class Command(BaseCommand):
    help = 'Sync student placement status based on accepted job applications'

    def handle(self, *args, **options):
        self.stdout.write('Syncing student placement status...')
        
        updated_count = 0
        
        # Get all students with accepted applications
        students_with_acceptances = StudentProfile.objects.filter(
            applications__status='accepted'
        ).distinct()
        
        for student in students_with_acceptances:
            # Get all accepted applications for this student, ordered by package
            accepted_apps = JobApplication.objects.filter(
                student=student,
                status='accepted'
            ).select_related('job__company').order_by('-job__package_max')
            
            if accepted_apps.exists():
                # Use the highest package offer
                best_offer = accepted_apps.first()
                offer_count = accepted_apps.count()
                
                # Check if update needed
                needs_update = (
                    not student.is_placed or
                    student.placement_company != best_offer.job.company.name or
                    student.placement_package != best_offer.job.package_max
                )
                
                if needs_update:
                    student.is_placed = True
                    student.placement_company = best_offer.job.company.name
                    student.placement_package = best_offer.job.package_max
                    student.save()
                    updated_count += 1
                    
                    if offer_count > 1:
                        companies = ', '.join([app.job.company.name for app in accepted_apps])
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Updated {student.user.get_full_name()} - {offer_count} offers: {companies} '
                                f'(Showing best: {best_offer.job.company.name} @ ₹{best_offer.job.package_max} LPA)'
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Marked {student.user.get_full_name()} as placed at {best_offer.job.company.name} '
                                f'@ ₹{best_offer.job.package_max} LPA'
                            )
                        )
        
        # Check for students marked as placed but with no accepted applications
        incorrectly_placed = StudentProfile.objects.filter(
            is_placed=True
        ).exclude(id__in=[s.id for s in students_with_acceptances])
        
        for student in incorrectly_placed:
            student.is_placed = False
            student.placement_company = None
            student.placement_package = None
            student.save()
            updated_count += 1
            self.stdout.write(
                self.style.WARNING(
                    f'✓ Unmarked {student.user.get_full_name()} - no accepted applications found'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Sync completed! Updated {updated_count} student(s).'
            )
        )