from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("pages", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="contactlead",
            name="deal_value",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=12,
                null=True,
                verbose_name="มูลค่าดีล (บาท)",
            ),
        ),
        migrations.AlterField(
            model_name="contactlead",
            name="status",
            field=models.CharField(
                choices=[
                    ("new", "New"),
                    ("contacted", "Contacted"),
                    ("qualified", "Qualified"),
                    ("proposal", "Proposal"),
                    ("closed_won", "Closed - Won"),
                    ("closed_lost", "Closed - Lost"),
                ],
                default="new",
                max_length=20,
                verbose_name="สถานะ",
            ),
        ),
    ]
