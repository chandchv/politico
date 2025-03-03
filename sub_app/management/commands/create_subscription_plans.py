from django.core.management.base import BaseCommand
from sub_app.models import SubscriptionPlan

class Command(BaseCommand):
    help = 'Creates initial subscription plans'

    def handle(self, *args, **kwargs):
        plans = [
            {
                'name': 'Standard Plan',
                'plan_type': 'standard',
                'price': 300000,
                'description': 'Entry-Level Luxury Wardrobe',
                'best_for': 'Young & Rich looking for trendy essentials, HNIs starting their wardrobe upgrade, or politicians/businessmen needing a foundational wardrobe.',
                'features': {
                    'services': [
                        'Personal Stylist (On request)',
                        'Annual wardrobe fit assessment'
                    ]
                }
            },
            {
                'name': 'Premium Plan',
                'plan_type': 'premium',
                'price': 500000,
                'description': 'Elevated Wardrobe for Business & Social Life',
                'best_for': 'HNIs in software/business, senior businessmen & politicians needing a refined wardrobe.',
                'features': {
                    'services': [
                        'Dedicated Personal Stylist',
                        'Quarterly consultations',
                        'Biannual wardrobe assessment'
                    ]
                }
            },
            {
                'name': 'Luxury Plan',
                'plan_type': 'luxury',
                'price': 700000,
                'description': 'Ultimate Wardrobe Experience',
                'best_for': 'HNIs, politicians, and elite businessmen who demand premium custom styling.',
                'features': {
                    'services': [
                        'Dedicated Personal Stylist',
                        'Monthly wardrobe curation',
                        'Quarterly wardrobe assessment',
                        '24/7 Emergency Wardrobe Support'
                    ]
                }
            }
        ]

        for plan_data in plans:
            SubscriptionPlan.objects.get_or_create(
                plan_type=plan_data['plan_type'],
                defaults=plan_data
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {plan_data["name"]}')
            ) 