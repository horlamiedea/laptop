# Generated by Django 2.2.16 on 2020-09-06 22:22

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('paystack', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymenthistory',
            name='data',
            field=jsonfield.fields.JSONField(),
        ),
    ]
