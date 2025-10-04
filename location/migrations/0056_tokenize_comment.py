from django.db import migrations
import string, secrets


def backfill_location_tokens(apps, schema_editor):
  """
  Generate unique random tokens for all Location objects
  that do not yet have one.
  Safe to run multiple times; will skip records that already have a token.
  """
  alphabet = string.ascii_letters + string.digits

  def make_token(length=10):
    return ''.join(secrets.choice(alphabet) for _ in range(length))

  Comment = apps.get_model('location', 'Comment')

  for obj in Comment.objects.filter(token__isnull=True) | Comment.objects.filter(token=''):
    new_token = make_token()
    # Ensure uniqueness
    while Comment.objects.filter(token=new_token).exists():
      new_token = make_token()
    obj.token = new_token
    obj.save(update_fields=['token'])

  print(f"[backfill_location_tokens] Updated tokens for {Comment.objects.filter(token__isnull=False).count()} records.")


class Migration(migrations.Migration):

  dependencies = [
      # 👇 update this to the most recent migration of your 'locations' app
      ('location', '0055_alter_comment_options_and_more'),
  ]

  operations = [
      migrations.RunPython(backfill_location_tokens, reverse_code=migrations.RunPython.noop),
  ]
