
from desktop.celery import app


'''
Common utility tasks

Example: generic run Django command install examples, document_clean-up, ldap_sync
'''

from notebook.management.commands.send_query_stats import Command


@app.task(ignore_result=True)
def execute_command(command_name):
  pass
