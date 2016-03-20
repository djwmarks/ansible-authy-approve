# Ansible authy\_approve Module

A prototype Ansible plugin that uses Authy's OneTouch API for 2FA.

The task will send an approval request to every listed Authy ID. If any of the
requests is authorised, the task succeeds. If any of the requests are declined
or a timer expires, the task fails.
