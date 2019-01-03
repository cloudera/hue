python-pam
==========

Python pam module supporting py3 (and py2)

Commandline example:

```
[david@Scott python-pam]$ python pam.py
Username: david
Password: 
0 Success

[david@Scott python-pam]$ python2 pam.py
Username: david
Password: 
0 Success
```

Inline examples:
```
[david@Scott python-pam]$ python
Python 3.4.1 (default, May 19 2014, 17:23:49)
[GCC 4.9.0 20140507 (prerelease)] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import pam
>>> p = pam.pam()
>>> p.authenticate('david', 'correctpassword')
True
>>> p.authenticate('david', 'badpassword')
False
>>> p.authenticate('david', 'correctpassword', service='login')
True
>>> p.authenticate('david', 'correctpassword', service='unknownservice')
False
>>> p.authenticate('david', 'correctpassword', service='login', resetcreds=True)
True
>>> p.authenticate('david', 'correctpassword', encoding='latin-1')
True
>>> print('{} {}'.format(p.code, p.reason))
0 Success
>>> p.authenticate('david', 'badpassword')
False
>>> print('{} {}'.format(p.code, p.reason))
7 Authentication failure
>>>
```
