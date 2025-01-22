# Security Policy

You can find more information on security incidents
on the [IdPy security webpage](https://idpy.org/security/).

You read on the [incident response policy](https://github.com/IdentityPython/Governance/blob/master/idpy-incidentresponse.md)
under the [governance documentation](https://github.com/IdentityPython/Governance).


## Incident report / Reporting a Vulnerability

Anyone can submit a potential security vulnerability to `incident-response@idpy.org`.
The incident-response team will verify the issue and contact you on how this will be
handled.


## Public Discussions

When a new vulnerability is reported and verified, a new security advisory is created on
GitHub and the issue is assigned a CVE identifier. Progress on the mitigation is tracked
on a private fork, where the incident-response team and developers communicate to fix
the issue.

When the fix is ready, a release plan is prepared and all communication channels are
used to notify the community of the presence of a new issue and the expected release
plan. This allows the community time to prepare for a security upgrade. (Notice that
security fixes are not backported at the moment.)

When the advisory is published, GitHub automatically notifies all associated projects of
the published advisory. Projects that use IdPy projects as dependencies should
automatically get Pull Requests by dependabot. Additionally, all communication channels
are used again, to notify the community of the release of a new version of the affected
software that contains the relevant fixes that mitigate the reported issue.


## Supported versions

Notice, that security fixes are not backported at the moment to older releases than the
latest. The team does not have the capacity to guarantee that these backports will exist.
You are advised to be prepared to upgrade to the latest version once the fix is out.
