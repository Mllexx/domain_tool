# Generated by Django 4.2.7 on 2023-12-19 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('domain_app', '0003_remove_user_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=30, null=True),
        ),
    ]