from django.core.management.base import BaseCommand
from sub_app.models import SubscriptionPlan, PlanCategory, PlanItem

class Command(BaseCommand):
    help = 'Creates initial plan items for each subscription plan'

    def handle(self, *args, **kwargs):
        # Create categories first
        categories = {
            'formal': 'Formal & Business Wear',
            'casual': 'Casual & Seasonal Wear',
            'ethnic': 'Ethnic & Occasion Wear',
            'accessories': 'Accessories & Footwear',
            'sleepwear': 'Sleepwear & Undergarments',
        }
        
        category_objects = {}
        for category_type, name in categories.items():
            cat, created = PlanCategory.objects.get_or_create(
                category_type=category_type,
                defaults={'name': name}
            )
            category_objects[category_type] = cat
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {name}'))

        # Define items for each plan
        plan_items = {
            'standard': {
                'formal': [
                    ('Custom-fitted dress shirt', 5),
                    ('Tailored suit', 2),
                    ('Tailored trousers', 2),
                    ('Premium polo shirt', 2),
                    ('Lightweight blazer', 1),
                ],
                'casual': [
                    ('Trendy T-shirt', 5),
                    ('Cuban collar shirt', 2),
                    ('Premium jeans/chinos', 3),
                    ('Bomber jacket', 1),
                ],
                'ethnic': [
                    ('Classic Sherwani/Jodhpuri suit', 1),
                    ('Silk kurta set', 1),
                ],
                'accessories': [
                    ('Premium belt', 1),
                    ('Formal shoes', 1),
                    ('Sneakers', 1),
                    ('Office bag', 1),
                ],
            },
            'premium': {
                'formal': [
                    ('Custom-fitted dress shirt', 10),
                    ('Tailored suit', 4),
                    ('Tailored trousers', 5),
                    ('Premium polo shirt', 5),
                    ('Lightweight blazer', 2),
                    ('Cashmere sweater', 2),
                ],
                'casual': [
                    ('Luxury T-shirt', 7),
                    ('Cuban collar shirt', 3),
                    ('Premium jeans/chinos', 5),
                    ('Tech jacket', 1),
                    ('Designer athleisure set', 1),
                ],
                'ethnic': [
                    ('Sherwani/Bandhgala', 2),
                    ('Silk kurta set', 2),
                    ('Indo-Western fusion set', 1),
                ],
                'accessories': [
                    ('Premium belt', 2),
                    ('Formal shoes', 2),
                    ('Sneakers', 2),
                    ('Premium sandals', 1),
                    ('Office/Travel bag', 2),
                    ('Sunglasses', 2),
                    ('Luxury watch', 1),
                ],
            },
            'luxury': {
                'formal': [
                    ('Custom-fitted dress shirt', 15),
                    ('Tailored suit', 6),
                    ('Tailored trousers', 7),
                    ('Premium polo shirt', 7),
                    ('High-end blazer', 3),
                    ('Luxury cashmere sweater', 3),
                ],
                'casual': [
                    ('Designer T-shirt', 10),
                    ('Cuban collar shirt', 5),
                    ('Premium jeans/chinos', 7),
                    ('Tech jacket', 2),
                    ('Designer athleisure set', 2),
                ],
                'ethnic': [
                    ('Sherwani/Bandhgala', 3),
                    ('Premium silk kurta set', 3),
                    ('Indo-Western fusion set', 2),
                ],
                'accessories': [
                    ('Luxury belt', 3),
                    ('Formal shoes', 3),
                    ('Luxury sneakers', 3),
                    ('Premium sandals', 2),
                    ('Office/Travel bag', 3),
                    ('Sunglasses', 3),
                    ('High-end watch', 2),
                    ('Luxury fountain pen', 1),
                ],
            },
        }

        # Create items for each plan
        for plan_type, categories_data in plan_items.items():
            try:
                plan = SubscriptionPlan.objects.get(plan_type=plan_type)
                for category_type, items in categories_data.items():
                    category = category_objects[category_type]
                    for item_name, quantity in items:
                        item, created = PlanItem.objects.get_or_create(
                            plan=plan,
                            category=category,
                            name=item_name,
                            defaults={
                                'quantity': quantity,
                                'description': f'{quantity}x {item_name} for {plan.name}',
                                'specifications': {'quantity': quantity}
                            }
                        )
                        if created:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Added {quantity}x {item_name} to {plan.name}'
                                )
                            )
            except SubscriptionPlan.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Plan type {plan_type} not found')
                ) 