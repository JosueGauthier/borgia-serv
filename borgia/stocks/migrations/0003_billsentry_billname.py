# Generated by Django 4.0.4 on 2023-09-01 09:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0002_billsentry'),
    ]

    operations = [
        migrations.AddField(
            model_name='billsentry',
            name='billname',
            field=models.TextField(default='Test init',
                                   verbose_name='Bill name'),
            preserve_default=False,
        ),
    ]
