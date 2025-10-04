from django.db import migrations
import string, secrets


def backfill_all_tokens(apps, schema_editor):
  """
  Backfill unique tokens for all models that define a 'token' field.
  Safe to run multiple times; skips existing tokens and ensures uniqueness.
  """

  alphabet = string.ascii_letters + string.digits

  def make_token(length=10):
    """Generate a short random token."""
    return ''.join(secrets.choice(alphabet) for _ in range(length))

  # Keep count for reporting
  total_updated = 0
  models_updated = []

  for model in apps.get_models():
    # Skip proxy and unmanaged models
    if not getattr(model._meta, 'managed', True):
      continue

    # Only process models that have a 'token' field
    token_fields = [f for f in model._meta.fields if f.name == 'token']
    if not token_fields:
      continue

    missing = model.objects.filter(token__isnull=True) | model.objects.filter(token='')
    count = missing.count()
    if not count:
      continue

    print(f"[backfill_all_tokens] {model.__name__}: found {count} missing tokens")

    for obj in missing.iterator():
      new_token = make_token()
      # Ensure uniqueness per model
      while model.objects.filter(token=new_token).exists():
        new_token = make_token()
      obj.token = new_token
      obj.save(update_fields=['token'])
      total_updated += 1

    models_updated.append(model.__name__)

  print(f"[backfill_all_tokens] ✅ Completed: {total_updated} tokens updated across {len(models_updated)} models: {', '.join(models_updated)}")


class Migration(migrations.Migration):

  dependencies = [
      ('location', '0057_rename_date_added_description_date_created_and_more'),
  ]

  operations = [
      migrations.RunPython(backfill_all_tokens, reverse_code=migrations.RunPython.noop),
  ]
