from django.db import migrations
import string, secrets


def regenerate_all_tokens(apps, schema_editor):
  """
  Regenerate unique random tokens for all models that define a 'token' field.
  Overwrites existing values (used when initial default duplicated tokens).
  """

  alphabet = string.ascii_letters + string.digits

  def make_token(length=10):
    return ''.join(secrets.choice(alphabet) for _ in range(length))

  total_updated = 0
  models_updated = []

  for model in apps.get_models():
    if not getattr(model._meta, 'managed', True):
      continue

    token_fields = [f for f in model._meta.fields if f.name == 'token']
    if not token_fields:
      continue

    print(f"[regenerate_all_tokens] Updating {model.__name__} tokens...")
    for obj in model.objects.all().iterator():
      new_token = make_token()
      # ensure uniqueness within model
      while model.objects.filter(token=new_token).exists():
        new_token = make_token()
      obj.token = new_token
      obj.save(update_fields=['token'])
      total_updated += 1

    models_updated.append(model.__name__)

  print(f"[regenerate_all_tokens] ✅ Completed: {total_updated} tokens updated across {len(models_updated)} models: {', '.join(models_updated)}")


class Migration(migrations.Migration):

  dependencies = [
      ('location', '0058_global_backfill_of_tokens'),
  ]

  operations = [
      migrations.RunPython(regenerate_all_tokens, reverse_code=migrations.RunPython.noop),
  ]
