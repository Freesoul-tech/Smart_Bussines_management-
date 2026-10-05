from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("businesses", "0007_business_latitude_business_longitude_and_more"),
        ("customers", "0001_initial"),
        ("reservations", "0002_reservation_customer"),
    ]
    operations = [
        migrations.CreateModel(
            name="Vehicle",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("registration_number", models.CharField(max_length=30)),
                ("vehicle_type", models.CharField(choices=[("car", "Car"), ("motorcycle", "Motorcycle"), ("van", "Van"), ("truck", "Truck"), ("other", "Other")], default="car", max_length=20)),
                ("description", models.CharField(blank=True, max_length=255)),
                ("is_checked_in", models.BooleanField(default=False)),
                ("checked_in_at", models.DateTimeField(blank=True, null=True)),
                ("checked_out_at", models.DateTimeField(blank=True, null=True)),
                ("business", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="motel_vehicles", to="businesses.business")),
                ("customer", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="motel_vehicles", to="customers.customer")),
                ("reservation", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="vehicles", to="reservations.reservation")),
            ],
            options={"ordering": ["registration_number"]},
        ),
        migrations.CreateModel(
            name="ParkingSpace",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("space_number", models.CharField(max_length=20)),
                ("status", models.CharField(choices=[("available", "Available"), ("maintenance", "Maintenance")], default="available", max_length=20)),
                ("assigned_at", models.DateTimeField(blank=True, null=True)),
                ("business", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="parking_spaces", to="businesses.business")),
                ("current_vehicle", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="parking_space", to="motel.vehicle")),
            ],
            options={"ordering": ["space_number"]},
        ),
        migrations.AddConstraint(
            model_name="vehicle",
            constraint=models.UniqueConstraint(fields=("business", "registration_number"), name="unique_motel_vehicle_registration"),
        ),
        migrations.AddConstraint(
            model_name="parkingspace",
            constraint=models.UniqueConstraint(fields=("business", "space_number"), name="unique_motel_parking_space"),
        ),
    ]
