from django.db import migrations
from django.contrib.postgres.operations import HStoreExtension


class Migration(migrations.Migration):

    dependencies = [("users", "0001_initial")]
    operations = [
        HStoreExtension()
    ]
