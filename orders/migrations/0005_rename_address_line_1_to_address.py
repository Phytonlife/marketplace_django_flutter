from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_remove_order_address_order_address_line_1'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='address_line_1',
            new_name='address',
        ),
    ]
