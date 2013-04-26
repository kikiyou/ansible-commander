# Copyright (c) 2013 AnsibleWorks, Inc.
#
# This file is part of Ansible Commander.
# 
# Ansible Commander is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License. 
#
# Ansible Commander is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Ansible Commander. If not, see <http://www.gnu.org/licenses/>.


import os
import shutil
import tempfile
from django.conf import settings
from django.test.utils import override_settings
from lib.main.models import *
from lib.main.tests.base import BaseTransactionTest
from lib.main.tasks import RunJob

TEST_PLAYBOOK = '''- hosts: test-group
  gather_facts: False
  tasks:
  - name: should pass
    command: test 1 = 1
  - name: should also pass
    command: test 2 = 2
'''

TEST_PLAYBOOK2 = '''- hosts: test-group
  gather_facts: False
  tasks:
  - name: should fail
    command: test 1 = 0
'''

TEST_SSH_KEY_DATA = '''-----BEGIN RSA PRIVATE KEY-----
MIIEpQIBAAKCAQEAyQ8F5bbgjHvk4SZJsKI9OmJKMFxZqRhvx4LaqjLTKbBwRBsY
1/C00NPiZn70dKbeyV7RNVZxuzM6yd3D3lwTdbDu/eJ0x72t3ch+TdLt/aenyy10
IvZyhSlxCLDkDaVVPFYJOQzVS8TkdOi6ZHc+R0c0A+4ZE8OQ8C0zIKtUTHqRk4/v
gYK5guhNS0DdgWkBj6K+r/9D4bqdPTJPt4S7H75vb1tBgseiqftEkLYOhTK2gsCi
5uJgpG4zPQY4Kk/97dbW7pwcvPkr1rKkAwEJ27Bfo+DBv3oEx3SinpXQtOrH1aEO
RHSXldBaymdBtVLUhjxDlnnQ7Ps+fNX04R7N4QIDAQABAoIBAQClEDxbNyRqsVxa
q8BbzxZNVFxsD6Vceb9rIDa8/DT4SO4iO8zNm8QWnZ2FYDz5d/X3hGxlSa7dbVWa
XQJtD1K6kKPks4IEaejP58Ypxj20vWu4Fnz+Jy4lvLwb0n2n5lBv1IKF389NATw9
7sL3sB3lDsPZZiQYYbogNDuBWqc+kP0zD84bONsM/B2HMRm9BRv2UsZf+zKU4pTA
UqHffyjmw7LqHmbtVjwVcUsC+xcE4kCuWLvabFnTWOSnWECyIw2+trxKdwCXbfzG
s5rn4Dj+aEKimzFaRpTSVx6w4yw9xw/EjsSaZ88jKSpTP8ocCut6zv+P/JwlukEX
4A4FxqyxAoGBAOp3G9EIAAWijcIgO5OdiZNEqVyqd3yyPzT6d/q7bf4dpVCZiLNA
bRmge83aMc4g2Dpkn/++It3bDmnXXGg+BZSX5KT9JLklXchaw9phv9J0diZEUvYS
mSQafbUGIqYnYzns3TU0cbgITs1iVIEstHYjGr3J88nDG+HFCHboxa93AoGBANuG
cDFgyvm79+haK2fHhUCZgaFFYBpkpuz+zjDjzIytOzymWa2gD9jIa7mvdvoH2ge3
AVG0vy+n9cJaqJMuLkhdI01wVlqY9wvDHFyZCXyIvKVPMljKeTvCNGCupsG4R171
gSKT5ryOx58MGbE7knAZC+QWpwxFpdpbfej6g7NnAoGBAMz6ipAJbXN/tG0FnvAj
pxXfzizcPw/+CTI40tGaMMQbiN5ZC+CiL39bBUFnQ2mQ31jVheegg3zvuL8hb4EW
z+wjitoPEZ7nowC5EUaHdJr6BBzaWKkWg1nD6yhqj7ow7xfCE3YjPlQEt1fpYjV4
LuClOgi4WPCIKYUMq6TBRaprAoGAVrEjs0xPPApQH5EkXQp9BALbH23/Qs0G4sbJ
dKMxT0jGAPCMr7VrLKgRarXxXVImdy99NOAVNGO2+PbGZcEyA9/MJjO71nFb9mgp
1iOVjHmPThUVg90JvWC3QIsYTZ5RiR2Yzqfr0gDsslGb/9LPxLcPbBbKB12l3rKM
6amswvcCgYEAvgcSlTfAkI3ac8rB70HuDmSdqKblIiQjtPtT/ixXaFkZOmHRr4AE
KepMRDnaO/ldPDPEWCGqPzEM0t/0jS8/hCu3zLHHpZ+0LnHq+EXkOI0/GB4P+z5l
Vz3kouC0BTav0rCEnDop/cWMTiAp/XhKXfrTTTOra/F8l2xD8n/mnzY=
-----END RSA PRIVATE KEY-----'''

TEST_SSH_KEY_DATA_LOCKED = '''-----BEGIN RSA PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: AES-128-CBC,6B4E92AF4C29DE26FD8535D81825BDE6

pg8YplxPpfzgEGUiko34DGaYklyGyYKXjOrGFGyLoquNAVNFyewT34dDrZi0IAaE
79wMVcdlHbrJfZz8ML8I/ft6zM6BdlwZExH4y9DRAaktY3yIXxSvowBQ6ljh3wUy
M6m0afOfVjT22V8hLFgX0yTQ6P9zTG1cmj6+JQWTsMJ5EP3rnFK5CyrJXP48B3GI
GgE66rkXDvcKlVeIrbrpcTyfmEpafPgVRJYCDFXxeO/BfKgUFVxFq1PgFbvGQMmD
wA6EsyRrN+aoub1sqzj8tM8e4nwEi0EifdRShkFeqH4GUOKypanTXfCqwFBgYi5a
i3YwSnniZZPwCniGR5cl8oetrc5dubq/IR0txsGi2lO6zJEWdSer/EadS0QAll4S
yXrSc/lFaez1VmVe/8aoBKDOHhe7jV3YXAuqCeB4o/SThB/9Gad44MTbqFH3d7cD
k+F0Cjup7LZqZpXeB7ZHRG/Yt9MtBzwDVmEWaxA1WIN5a8xyZEVzRswSi4lZX69z
Va7eTKcrCbHOQmIbLZGRiZbAbfgriwwxQCJWELv80h+A754Bhi23n3WzcT094fRi
cqK//HcHHXxYGmrfUbHYcj+GCQ07Uk2ZR3qglmPISUCgfZwM9k0LpXudWE8vmF2S
pAnbgxgrfUMtpu5EAO+d8Sn5wQLVD7YzPBUhM4PYfYUbJnRoZQryuR4lqCzcg0te
BM8x1LzSXyBEbQaonuMzSz1hCQ9hZpUwUEqDWAT3cPNmgyWkXQ1P8ehJhTmryGJw
/GHxNzMZDGj+bBKo7ic3r1g3ZmmlSU1EVxMLvRBKhdc1XicBVqepDma6/LEpj+5X
oplR+3Q0QSQ8CchcSxYtOpI3UBCatpyu09GtfzS+7bI5I7FVYUccR83+oQlKpPHC
5O2irB8JeXqAY679fx2N4i0E6l5Xr5AjUtOBCNil0Y70eOf9ER6i7kGakR7bUtk5
fQn8Em9pLsYYalnekn4sxyHpGq59KgNPjQiJRByYidSJ/oyNbmtPlxfXLwpuicd2
8HLm1e0UeGidfF/bSlySwDzy1ZlSr/Apdcn9ou5hfhaGuQvjr9SvJwxQFNRMPdHj
ukBSDGuxyyU+qBrWJhFsymiZAWDofY/4GzgMu4hh0PwN5arzoTxnLHmc/VFttyMx
nP7bTaa9Sr54TlMr7NuKTzz5biXKjqJ9AZKIUF2+ERebjV0hMpJ5NPsLwPUnA9kx
R3tl1JL2Ia82ovS81Ghff/cBZsx/+LQYa+ac4eDTyXxyg4ei5tPwOlzz7pDKJAr9
XEh2X6rywCNghEMZPaOQLiEDLJ2is6P4OarSa/yoU4OMetpFfwZ0oJSCmGlEa+CF
zeJ80yXhU1Ru2eqiUjCAUg25BFPwoiMJDc6jWWow7OrXCQsw7Ddo2ncy1p9QeWjM
2R4ojPHWuXKYxvwVSc8NZHASlycBCaxHLDAEyH4avOSDPWOB1H5t+RrNmo0qgush
0aRo6F7BjzB2rA4E+xu2u11TBfF8iB3PC919/vxnkXF97NqezsaCz6VbRlsU0A+B
wwoi+P4JlJF6ZuhuDv6mhmBCSdXdc1bvimvdpOljhThr+cG5mM08iqWGKdA665cw
-----END RSA PRIVATE KEY-----
'''

TEST_SSH_KEY_DATA_UNLOCK = 'unlockme'

@override_settings(CELERY_ALWAYS_EAGER=True,
                   CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
class BaseCeleryTest(BaseTransactionTest):
    '''
    Base class for celery task tests.
    '''

@override_settings(ANSIBLE_TRANSPORT='local')
class RunJobTest(BaseCeleryTest):
    '''
    Test cases for RunJob celery task.
    '''

    def setUp(self):
        super(RunJobTest, self).setUp()
        self.test_project_path = None
        self.setup_users()
        self.organization = self.make_organizations(self.super_django_user, 1)[0]
        self.inventory = Inventory.objects.create(name='test-inventory',
                                                  description='description for test-inventory',
                                                  organization=self.organization)
        self.host = self.inventory.hosts.create(name='host.example.com',
                                                inventory=self.inventory)
        self.group = self.inventory.groups.create(name='test-group',
                                                  inventory=self.inventory)
        self.group.hosts.add(self.host)
        self.project = None
        self.credential = None
        # Pass test database name in environment for use by the inventory script.
        os.environ['ACOM_TEST_DATABASE_NAME'] = settings.DATABASES['default']['NAME']
        # Monkeypatch RunJob to capture list of command line arguments.
        self.original_build_args = RunJob.build_args
        self.run_job_args = None
        def new_build_args(_self, job, **kw):
            args = self.original_build_args(_self, job, **kw)
            self.run_job_args = args
            return args
        RunJob.build_args = new_build_args

    def tearDown(self):
        super(RunJobTest, self).tearDown()
        os.environ.pop('ACOM_TEST_DATABASE_NAME', None)
        if self.test_project_path:
            shutil.rmtree(self.test_project_path, True)
        RunJob.build_args = self.original_build_args

    def create_test_credential(self, **kwargs):
        opts = {
            'name': 'test-creds',
            'user': self.super_django_user,
            'ssh_username': '',
            'ssh_key_data': '',
            'ssh_key_unlock': '',
            'ssh_password': '',
            'sudo_username': '',
            'sudo_password': '',
        }
        opts.update(kwargs)
        self.credential = Credential.objects.create(**opts)
        return self.credential

    def create_test_project(self, playbook_content):
        self.project = self.make_projects(self.normal_django_user, 1, playbook_content)[0]
        self.organization.projects.add(self.project)

    def create_test_job_template(self, **kwargs):
        opts = {
            'name': 'test-job-template',
            'inventory': self.inventory,
            'project': self.project,
            'credential': self.credential,
        }
        try:
            opts['playbook'] = self.project.available_playbooks[0]
        except (AttributeError, IndexError):
            pass
        opts.update(kwargs)
        self.job_template = JobTemplate.objects.create(**opts)
        return self.job_template

    def create_test_job(self, **kwargs):
        job_template = kwargs.pop('job_template', None)
        if job_template:
            self.job = job_template.create_job(**kwargs)
        else:
            opts = {
                'name': 'test-job',
                'inventory': self.inventory,
                'project': self.project,
                'credential': self.credential,
            }
            try:
                opts['playbook'] = self.project.available_playbooks[0]
            except (AttributeError, IndexError):
                pass
            opts.update(kwargs)
            self.job = Job.objects.create(**opts)
        return self.job

    def test_run_job(self):
        self.create_test_project(TEST_PLAYBOOK)
        job_template = self.create_test_job_template()
        job = self.create_test_job(job_template=job_template)
        self.assertEqual(job.status, 'new')
        self.assertFalse(job.get_passwords_needed_to_start())
        self.assertTrue(job.start())
        self.assertEqual(job.status, 'pending')
        job = Job.objects.get(pk=job.pk)
        #print 'stdout:', job.result_stdout
        #print 'stderr:', job.result_stderr
        #print job.status
        #print settings.DATABASES
        #print self.run_job_args
        self.assertEqual(job.status, 'successful')
        self.assertTrue(job.result_stdout)
        job_events = job.job_events.all()
        self.assertEqual(job_events.filter(event='playbook_on_start').count(), 1)
        self.assertEqual(job_events.filter(event='playbook_on_play_start').count(), 1)
        self.assertEqual(job_events.filter(event='playbook_on_task_start').count(), 2)
        self.assertEqual(job_events.filter(event='runner_on_ok').count(), 2)
        for evt in job_events.filter(event='runner_on_ok'):
            self.assertEqual(evt.host, self.host)
        self.assertEqual(job_events.filter(event='playbook_on_stats').count(), 1)
        self.assertEqual(job.successful_hosts.count(), 1)
        self.assertEqual(job.failed_hosts.count(), 0)
        self.assertEqual(job.changed_hosts.count(), 1)
        self.assertEqual(job.unreachable_hosts.count(), 0)
        self.assertEqual(job.skipped_hosts.count(), 0)
        self.assertEqual(job.processed_hosts.count(), 1)

    def test_check_job(self):
        self.create_test_project(TEST_PLAYBOOK)
        job_template = self.create_test_job_template()
        job = self.create_test_job(job_template=job_template, job_type='check')
        self.assertEqual(job.status, 'new')
        self.assertFalse(job.get_passwords_needed_to_start())
        self.assertTrue(job.start())
        self.assertEqual(job.status, 'pending')
        job = Job.objects.get(pk=job.pk)
        self.assertEqual(job.status, 'successful')
        self.assertTrue(job.result_stdout)
        job_events = job.job_events.all()
        self.assertEqual(job_events.filter(event='playbook_on_start').count(), 1)
        self.assertEqual(job_events.filter(event='playbook_on_play_start').count(), 1)
        self.assertEqual(job_events.filter(event='playbook_on_task_start').count(), 2)
        self.assertEqual(job_events.filter(event='runner_on_skipped').count(), 2)
        for evt in job_events.filter(event='runner_on_skipped'):
            self.assertEqual(evt.host, self.host)
        self.assertEqual(job_events.filter(event='playbook_on_stats').count(), 1)
        self.assertEqual(job.successful_hosts.count(), 0)
        self.assertEqual(job.failed_hosts.count(), 0)
        self.assertEqual(job.changed_hosts.count(), 0)
        self.assertEqual(job.unreachable_hosts.count(), 0)
        self.assertEqual(job.skipped_hosts.count(), 1)
        self.assertEqual(job.processed_hosts.count(), 1)

    def test_run_job_that_fails(self):
        self.create_test_project(TEST_PLAYBOOK2)
        job_template = self.create_test_job_template()
        job = self.create_test_job(job_template=job_template)
        self.assertEqual(job.status, 'new')
        self.assertFalse(job.get_passwords_needed_to_start())
        self.assertTrue(job.start())
        self.assertEqual(job.status, 'pending')
        job = Job.objects.get(pk=job.pk)
        self.assertEqual(job.status, 'failed')
        self.assertTrue(job.result_stdout)
        job_events = job.job_events.all()
        self.assertEqual(job_events.filter(event='playbook_on_start').count(), 1)
        self.assertEqual(job_events.filter(event='playbook_on_play_start').count(), 1)
        self.assertEqual(job_events.filter(event='playbook_on_task_start').count(), 1)
        self.assertEqual(job_events.filter(event='runner_on_failed').count(), 1)
        self.assertEqual(job_events.get(event='runner_on_failed').host, self.host)
        self.assertEqual(job_events.filter(event='playbook_on_stats').count(), 1)
        self.assertEqual(job.successful_hosts.count(), 0)
        self.assertEqual(job.failed_hosts.count(), 1)
        self.assertEqual(job.changed_hosts.count(), 0)
        self.assertEqual(job.unreachable_hosts.count(), 0)
        self.assertEqual(job.skipped_hosts.count(), 0)
        self.assertEqual(job.processed_hosts.count(), 1)

    def test_check_job_where_task_would_fail(self):
        self.create_test_project(TEST_PLAYBOOK2)
        job_template = self.create_test_job_template()
        job = self.create_test_job(job_template=job_template, job_type='check')
        self.assertEqual(job.status, 'new')
        self.assertFalse(job.get_passwords_needed_to_start())
        self.assertTrue(job.start())
        self.assertEqual(job.status, 'pending')
        job = Job.objects.get(pk=job.pk)
        # Since we don't actually run the task, the --check should indicate
        # everything is successful.
        self.assertEqual(job.status, 'successful')
        self.assertTrue(job.result_stdout)
        job_events = job.job_events.all()
        self.assertEqual(job_events.filter(event='playbook_on_start').count(), 1)
        self.assertEqual(job_events.filter(event='playbook_on_play_start').count(), 1)
        self.assertEqual(job_events.filter(event='playbook_on_task_start').count(), 1)
        self.assertEqual(job_events.filter(event='runner_on_skipped').count(), 1)
        self.assertEqual(job_events.get(event='runner_on_skipped').host, self.host)
        self.assertEqual(job_events.filter(event='playbook_on_stats').count(), 1)
        self.assertEqual(job.successful_hosts.count(), 0)
        self.assertEqual(job.failed_hosts.count(), 0)
        self.assertEqual(job.changed_hosts.count(), 0)
        self.assertEqual(job.unreachable_hosts.count(), 0)
        self.assertEqual(job.skipped_hosts.count(), 1)
        self.assertEqual(job.processed_hosts.count(), 1)

    def test_cancel_job(self):
        self.create_test_project(TEST_PLAYBOOK)
        job_template = self.create_test_job_template()
        # The cancel_flag isn't checked until after the job is started, so
        # setting it here will allow the job to start, then interrupt it.
        job = self.create_test_job(job_template=job_template, cancel_flag=True)
        self.assertEqual(job.status, 'new')
        self.assertFalse(job.get_passwords_needed_to_start())
        self.assertTrue(job.start())
        self.assertEqual(job.status, 'pending')
        job = Job.objects.get(pk=job.pk)
        self.assertEqual(job.status, 'canceled')

    def test_extra_job_options(self):
        self.create_test_project(TEST_PLAYBOOK)
        job_template = self.create_test_job_template(use_sudo=True, forks=3,
                                                     verbosity=2,
                                                     extra_vars={'foo': 1})
        job = self.create_test_job(job_template=job_template)
        self.assertEqual(job.status, 'new')
        self.assertFalse(job.get_passwords_needed_to_start())
        self.assertTrue(job.start())
        self.assertEqual(job.status, 'pending')
        job = Job.objects.get(pk=job.pk)
        # Job may fail if current user doesn't have password-less sudo
        # privileges, but we're mainly checking the command line arguments.
        self.assertTrue(job.status in ('successful', 'failed'))
        self.assertTrue(job.result_stdout)
        self.assertTrue('--sudo' in self.run_job_args)
        self.assertTrue('--forks=3' in self.run_job_args)
        self.assertTrue('-vv' in self.run_job_args)
        self.assertTrue('--extra-vars=foo=1' in self.run_job_args)

    def test_limit_option(self):
        self.create_test_project(TEST_PLAYBOOK)
        job_template = self.create_test_job_template(limit='bad.example.com')
        job = self.create_test_job(job_template=job_template)
        self.assertEqual(job.status, 'new')
        self.assertFalse(job.get_passwords_needed_to_start())
        self.assertTrue(job.start())
        self.assertEqual(job.status, 'pending')
        job = Job.objects.get(pk=job.pk)
        self.assertEqual(job.status, 'failed')
        self.assertTrue('--limit=bad.example.com' in self.run_job_args)

    def test_ssh_username_and_password(self):
        self.create_test_credential(ssh_username='sshuser',
                                    ssh_password='sshpass')
        self.create_test_project(TEST_PLAYBOOK)
        job_template = self.create_test_job_template()
        job = self.create_test_job(job_template=job_template)
        self.assertEqual(job.status, 'new')
        self.assertFalse(job.get_passwords_needed_to_start())
        self.assertTrue(job.start())
        self.assertEqual(job.status, 'pending')
        job = Job.objects.get(pk=job.pk)
        self.assertEqual(job.status, 'successful')
        self.assertTrue('--user=sshuser' in self.run_job_args)
        self.assertTrue('--ask-pass' in self.run_job_args)

    def test_ssh_ask_password(self):
        self.create_test_credential(ssh_password='ASK')
        self.create_test_project(TEST_PLAYBOOK)
        job_template = self.create_test_job_template()
        job = self.create_test_job(job_template=job_template)
        self.assertEqual(job.status, 'new')
        self.assertTrue(job.get_passwords_needed_to_start())
        self.assertTrue('ssh_password' in job.get_passwords_needed_to_start())
        self.assertFalse(job.start())
        self.assertEqual(job.status, 'new')
        self.assertTrue(job.start(ssh_password='sshpass'))
        self.assertEqual(job.status, 'pending')
        job = Job.objects.get(pk=job.pk)
        self.assertEqual(job.status, 'successful')
        self.assertTrue('--ask-pass' in self.run_job_args)

    def test_sudo_username_and_password(self):
        self.create_test_credential(sudo_username='sudouser',
                                    sudo_password='sudopass')
        self.create_test_project(TEST_PLAYBOOK)
        job_template = self.create_test_job_template()
        job = self.create_test_job(job_template=job_template)
        self.assertEqual(job.status, 'new')
        self.assertFalse(job.get_passwords_needed_to_start())
        self.assertTrue(job.start())
        self.assertEqual(job.status, 'pending')
        job = Job.objects.get(pk=job.pk)
        # Job may fail if current user doesn't have password-less sudo
        # privileges, but we're mainly checking the command line arguments.
        self.assertTrue(job.status in ('successful', 'failed'))
        self.assertTrue('--sudo-user=sudouser' in self.run_job_args)
        self.assertTrue('--ask-sudo-pass' in self.run_job_args)

    def test_sudo_ask_password(self):
        self.create_test_credential(sudo_password='ASK')
        self.create_test_project(TEST_PLAYBOOK)
        job_template = self.create_test_job_template()
        job = self.create_test_job(job_template=job_template)
        self.assertEqual(job.status, 'new')
        self.assertTrue(job.get_passwords_needed_to_start())
        self.assertTrue('sudo_password' in job.get_passwords_needed_to_start())
        self.assertFalse(job.start())
        self.assertEqual(job.status, 'new')
        self.assertTrue(job.start(sudo_password='sudopass'))
        self.assertEqual(job.status, 'pending')
        job = Job.objects.get(pk=job.pk)
        # Job may fail if current user doesn't have password-less sudo
        # privileges, but we're mainly checking the command line arguments.
        self.assertTrue(job.status in ('successful', 'failed'))
        self.assertTrue('--ask-sudo-pass' in self.run_job_args)

    def test_unlocked_ssh_key(self):
        self.create_test_credential(ssh_key_data=TEST_SSH_KEY_DATA)
        self.create_test_project(TEST_PLAYBOOK)
        job_template = self.create_test_job_template()
        job = self.create_test_job(job_template=job_template)
        self.assertEqual(job.status, 'new')
        self.assertFalse(job.get_passwords_needed_to_start())
        self.assertTrue(job.start())
        self.assertEqual(job.status, 'pending')
        job = Job.objects.get(pk=job.pk)
        self.assertEqual(job.status, 'successful')
        self.assertTrue('ssh-agent' in self.run_job_args)

    def test_locked_ssh_key_with_password(self):
        self.create_test_credential(ssh_key_data=TEST_SSH_KEY_DATA_LOCKED,
                                    ssh_key_unlock=TEST_SSH_KEY_DATA_UNLOCK)
        self.create_test_project(TEST_PLAYBOOK)
        job_template = self.create_test_job_template()
        job = self.create_test_job(job_template=job_template)
        self.assertEqual(job.status, 'new')
        self.assertFalse(job.get_passwords_needed_to_start())
        self.assertTrue(job.start())
        self.assertEqual(job.status, 'pending')
        job = Job.objects.get(pk=job.pk)
        self.assertEqual(job.status, 'successful')
        self.assertTrue('ssh-agent' in self.run_job_args)
        self.assertTrue('Bad passphrase' not in job.result_stdout)

    def test_locked_ssh_key_with_bad_password(self):
        self.create_test_credential(ssh_key_data=TEST_SSH_KEY_DATA_LOCKED,
                                    ssh_key_unlock='not the passphrase')
        self.create_test_project(TEST_PLAYBOOK)
        job_template = self.create_test_job_template()
        job = self.create_test_job(job_template=job_template)
        self.assertEqual(job.status, 'new')
        self.assertFalse(job.get_passwords_needed_to_start())
        self.assertTrue(job.start())
        self.assertEqual(job.status, 'pending')
        job = Job.objects.get(pk=job.pk)
        self.assertEqual(job.status, 'failed')
        self.assertTrue('ssh-agent' in self.run_job_args)
        self.assertTrue('Bad passphrase' in job.result_stdout)

    def test_locked_ssh_key_ask_password(self):
        self.create_test_credential(ssh_key_data=TEST_SSH_KEY_DATA_LOCKED,
                                    ssh_key_unlock='ASK')
        self.create_test_project(TEST_PLAYBOOK)
        job_template = self.create_test_job_template()
        job = self.create_test_job(job_template=job_template)
        self.assertEqual(job.status, 'new')
        self.assertTrue(job.get_passwords_needed_to_start())
        self.assertTrue('ssh_key_unlock' in job.get_passwords_needed_to_start())
        self.assertFalse(job.start())
        self.assertEqual(job.status, 'new')
        self.assertTrue(job.start(ssh_key_unlock=TEST_SSH_KEY_DATA_UNLOCK))
        self.assertEqual(job.status, 'pending')
        job = Job.objects.get(pk=job.pk)
        self.assertEqual(job.status, 'successful')
        self.assertTrue('ssh-agent' in self.run_job_args)
        self.assertTrue('Bad passphrase' not in job.result_stdout)
