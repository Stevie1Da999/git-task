import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('posts', '0001_initial'), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.DeleteModel(name='Post'),
        migrations.DeleteModel(name='Author'),
        migrations.CreateModel(name='Profile', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('account_type', models.CharField(choices=[('buyer','Buyer'),('vendor','Vendor')], max_length=10)),
            ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name='Store', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('name', models.CharField(max_length=120)), ('description', models.TextField(blank=True)),
            ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stores', to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name='Product', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('name', models.CharField(max_length=120)), ('description', models.TextField(blank=True)),
            ('price', models.DecimalField(decimal_places=2, max_digits=10)), ('stock', models.PositiveIntegerField(default=0)),
            ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='posts.store')),
        ]),
        migrations.CreateModel(name='Order', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('created_at', models.DateTimeField(auto_now_add=True)), ('total', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
            ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name='OrderItem', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('quantity', models.PositiveIntegerField()), ('price', models.DecimalField(decimal_places=2, max_digits=10)),
            ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='posts.order')),
            ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='posts.product')),
        ]),
        migrations.CreateModel(name='Review', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('rating', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
            ('comment', models.TextField()), ('verified', models.BooleanField(default=False)), ('created_at', models.DateTimeField(auto_now_add=True)),
            ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to=settings.AUTH_USER_MODEL)),
            ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='posts.product')),
        ]),
    ]
