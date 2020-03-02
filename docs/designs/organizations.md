# Organizations

Goal: support of more than one tenant per server instance [HUE-8530](https://issues.cloudera.org/browse/HUE-8530)

## Design

Add an `organization` model in `useradmin/models2.py` and have `User`, `Group` classes link to it.
Keep all the models in models2.py and do not change the current `useradmin/models.py` logic so that it is backward compatible.

e.g. How to import the organization models:

```
from useradmin.models import User, Group
```

Which under the cover does the switch between regular users and organizational users:

```
if ENABLE_ORGANIZATIONS.get():
  from useradmin.models import User, Group
else:
  from django.contrib.auth.models import User, Group
```

Notes:
* large organization would probably still need their own instances in a dedicated Kubernetes namespace
* dependencies: connector configuration, task server, kubernetes
* database migrations files can only be for v1 or v2 (due to Django internals). Migrations for v2 should replace v1 and so are omitted for now until the full completion of the functionality. This also means that a setup for organizations would need to be from scratch and not come from an upgrade of models v1.
