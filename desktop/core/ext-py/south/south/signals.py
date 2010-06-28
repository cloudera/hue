"""
South-specific signals
"""

from django.dispatch import Signal

# Sent at the start of the migration of an app
pre_migrate = Signal(providing_args=["app"])

# Sent after each successful migration of an app
post_migrate = Signal(providing_args=["app"])

# Sent after each run of a particular migration in a direction
ran_migration = Signal(providing_args=["app","migration","method"])
