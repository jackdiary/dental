"""
Management command to set up initial data for the dental AI system
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.clinics.models import Clinic

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up initial data for the dental AI system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-superuser',
            action='store_true',
            help='Create a superuser account',
        )
        parser.add_argument(
            '--create-sample-data',
            action='store_true',
            help='Create sample clinic data',
        )

    def handle(self, *args, **options):
        if options['create_superuser']:
            self.create_superuser()
        
        if options['create_sample_data']:
            self.create_sample_clinics()
        
        self.stdout.write(
            self.style.SUCCESS('Initial data setup completed successfully!')
        )

    def create_superuser(self):
        """Create a superuser if it doesn't exist"""
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@dentalai.com',
                password='admin123'
            )
            self.stdout.write(
                self.style.SUCCESS('Superuser created: admin / admin123')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Superuser already exists')
            )

    def create_sample_clinics(self):
        """Create sample clinic data"""
        sample_clinics = [
            {
                'name': '서울대학교치과병원',
                'address': '서울특별시 종로구 대학로 101',
                'district': '종로구',
                'latitude': 37.5838,
                'longitude': 127.0021,
                'phone': '02-2072-2175',
                'has_parking': True,
                'night_service': False,
                'weekend_service': True,
            },
            {
                'name': '강남세브란스치과',
                'address': '서울특별시 강남구 언주로 211',
                'district': '강남구',
                'latitude': 37.5172,
                'longitude': 127.0473,
                'phone': '02-2019-3300',
                'has_parking': True,
                'night_service': True,
                'weekend_service': False,
            },
            {
                'name': '연세대학교치과대학병원',
                'address': '서울특별시 서대문구 연세로 50-1',
                'district': '서대문구',
                'latitude': 37.5638,
                'longitude': 126.9407,
                'phone': '02-2228-8900',
                'has_parking': True,
                'night_service': False,
                'weekend_service': True,
            }
        ]

        for clinic_data in sample_clinics:
            clinic, created = Clinic.objects.get_or_create(
                name=clinic_data['name'],
                defaults=clinic_data
            )
            if created:
                self.stdout.write(f'Created clinic: {clinic.name}')
            else:
                self.stdout.write(f'Clinic already exists: {clinic.name}')