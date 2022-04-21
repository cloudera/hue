# Revert field drop to keep the DB backward compatible with old Hue


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('axes', '0006_remove_accesslog_trusted'),
    ]

    operations = [
        migrations.AddField(
            model_name='accesslog',
            name='trusted',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]

