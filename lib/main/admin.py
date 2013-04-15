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


import json

from django.conf.urls import *
from django.contrib import admin
from django.contrib.admin.util import unquote
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.utils.html import format_html
from lib.main.models import *

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

class UserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    readonly_fields = ('last_login', 'date_joined')
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

try:
    admin.site.unregister(User)
except admin.site.NotRegistered:
    pass
admin.site.register(User, UserAdmin)

# FIXME: Hide auth.Group admin

class OrganizationAdmin(admin.ModelAdmin):

    list_display = ('name', 'description', 'active')
    list_filter = ('active', 'tags')
    fieldsets = (
        (None, {'fields': ('name', 'active', 'created_by', 'description',)}),
        (_('Members'), {'fields': ('users', 'admins',)}),
        (_('Projects'), {'fields': ('projects',)}),
        (_('Tags'), {'fields': ('tags',)}),
        (_('Audit Trail'), {'fields': ('creation_date', 'audit_trail',)}),
    )
    readonly_fields = ('creation_date', 'audit_trail')
    filter_horizontal = ('users', 'admins', 'projects', 'tags')

class InventoryHostInline(admin.StackedInline):
    
    model = Host
    extra = 0
    fields = ('name', 'description', 'active', 'tags')
    filter_horizontal = ('tags',)

class InventoryGroupInline(admin.StackedInline):

    model = Group
    extra = 0
    fields = ('name', 'description', 'active', 'parents', 'hosts', 'tags')
    filter_horizontal = ('parents', 'hosts', 'tags')

class InventoryAdmin(admin.ModelAdmin):

    list_display = ('name', 'organization', 'description', 'active')
    list_filter = ('organization', 'active')
    fieldsets = (
        (None, {'fields': ('name', 'organization', 'active', 'created_by',
                           'description',)}),
        (_('Tags'), {'fields': ('tags',)}),
        (_('Audit Trail'), {'fields': ('creation_date', 'audit_trail',)}),
    )
    readonly_fields = ('creation_date', 'audit_trail')
    filter_horizontal = ('tags',)
    inlines = [InventoryHostInline, InventoryGroupInline]

class TagAdmin(admin.ModelAdmin):

    list_display = ('name',)

#class AuditTrailAdmin(admin.ModelAdmin):
#
#    list_display = ('name', 'description', 'active')
#    not currently on model, so disabling for now.
#    filter_horizontal = ('tags',)

class VariableDataInline(admin.StackedInline):

    model = VariableData
    extra = 0
    max_num = 1
    # FIXME: Doesn't yet work as inline due to the way the OneToOne field is
    # defined.

class LaunchJobHostSummaryInline(admin.TabularInline):

    model = LaunchJobHostSummary
    extra = 0
    can_delete = False

    def has_add_permission(self, request):
        return False

class LaunchJobStatusEventInline(admin.StackedInline):

    model = LaunchJobStatusEvent
    extra = 0
    can_delete = False

    def has_add_permission(self, request):
        return False

    def get_event_data_display(self, obj):
        return format_html('<pre class="json-display">{0}</pre>', json.dumps(obj.event_data, indent=4))
    get_event_data_display.short_description = _('Event data')
    get_event_data_display.allow_tags = True

class LaunchJobHostSummaryInlineForHost(LaunchJobHostSummaryInline):

    fields = ('launch_job_status', 'changed', 'dark', 'failures', 'ok', 'processed', 'skipped')
    readonly_fields = ('launch_job_status', 'changed', 'dark', 'failures', 'ok', 'processed', 'skipped')

class LaunchJobStatusEventInlineForHost(LaunchJobStatusEventInline):

    fields = ('created', 'event', 'get_event_data_display', 'launch_job_status')
    readonly_fields = ('created', 'event', 'get_event_data_display', 'launch_job_status')

class HostAdmin(admin.ModelAdmin):

    list_display = ('name', 'inventory', 'description', 'active')
    list_filter = ('inventory', 'active')
    fields = ('name', 'inventory', 'description', 'active', 'tags',
              'created_by', 'audit_trail')
    filter_horizontal = ('tags',)
    # FIXME: Edit reverse of many to many for groups.
    #inlines = [VariableDataInline]
    inlines = [LaunchJobHostSummaryInlineForHost, LaunchJobStatusEventInlineForHost]

class GroupAdmin(admin.ModelAdmin):

    list_display = ('name', 'description', 'active')
    filter_horizontal = ('parents', 'hosts', 'tags')
    #inlines = [VariableDataInline]

class VariableDataAdmin(admin.ModelAdmin):

    list_display = ('name', 'description', 'active')
    filter_horizontal = ('tags',)

class CredentialAdmin(admin.ModelAdmin):

    list_display = ('name', 'description', 'active')
    filter_horizontal = ('tags',)

class TeamAdmin(admin.ModelAdmin):

    list_display = ('name', 'description', 'active')
    filter_horizontal = ('projects', 'users', 'tags')

class ProjectAdmin(admin.ModelAdmin):

    list_display = ('name', 'description', 'active')
    filter_horizontal = ('tags',)

class PermissionAdmin(admin.ModelAdmin):

    list_display = ('name', 'description', 'active')
    filter_horizontal = ('tags',)

class LaunchJobAdmin(admin.ModelAdmin):

    list_display = ('name', 'description', 'active', 'get_start_link_display',
                    'get_statuses_link_display')
    fieldsets = (
        (None, {'fields': ('name', 'active', 'created_by', 'description',
                           'get_start_link_display', 'get_statuses_link_display')}),
        (_('Job Parameters'), {'fields': ('inventory', 'project', 'credential',
                                          'user', 'job_type')}),
        (_('Tags'), {'fields': ('tags',)}),
        (_('Audit Trail'), {'fields': ('creation_date', 'audit_trail',)}),
    )
    readonly_fields = ('creation_date', 'audit_trail', 'get_start_link_display',
                       'get_statuses_link_display')
    filter_horizontal = ('tags',)

    def get_start_link_display(self, obj):
        info = self.model._meta.app_label, self.model._meta.module_name
        start_url = reverse('admin:%s_%s_start' % info, args=(obj.pk,),
                            current_app=self.admin_site.name)
        return '<a href="%s">Run Job</a>' % start_url
    get_start_link_display.short_description = _('Run')
    get_start_link_display.allow_tags = True

    def get_statuses_link_display(self, obj):
        info = LaunchJobStatus._meta.app_label, LaunchJobStatus._meta.module_name
        statuses_url = reverse('admin:%s_%s_changelist' % info,
                               current_app=self.admin_site.name)
        statuses_url += '?launch_job__id__exact=%d' % obj.pk
        return '<a href="%s">View Logs</a>' % statuses_url
    get_statuses_link_display.short_description = _('Logs')
    get_statuses_link_display.allow_tags = True

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.module_name
        urls = super(LaunchJobAdmin, self).get_urls()
        return patterns('',
            url(r'^(.+)/start/$',
                self.admin_site.admin_view(self.start_job_view),
                name='%s_%s_start' % info),
        ) + urls

    def start_job_view(self, request, object_id):
        obj = self.get_object(request, unquote(object_id))
        ljs = obj.start()
        info = ljs._meta.app_label, ljs._meta.module_name
        status_url = reverse('admin:%s_%s_change' % info, args=(ljs.pk,),
                             current_app=self.admin_site.name)
        messages.success(request, '%s has been started.' % ljs)
        return HttpResponseRedirect(status_url)

class LaunchJobHostSummaryInlineForLaunchJobStatus(LaunchJobHostSummaryInline):

    fields = ('host', 'changed', 'dark', 'failures', 'ok', 'processed', 'skipped')
    readonly_fields = ('host', 'changed', 'dark', 'failures', 'ok', 'processed', 'skipped')

class LaunchJobStatusEventInlineForLaunchJobStatus(LaunchJobStatusEventInline):

    fields = ('created', 'event', 'get_event_data_display', 'host')
    readonly_fields = ('created', 'event', 'get_event_data_display', 'host')

class LaunchJobStatusAdmin(admin.ModelAdmin):

    list_display = ('name', 'launch_job', 'status')
    fields = ('name', 'get_launch_job_display', 'status',
              'get_result_stdout_display', 'get_result_stderr_display',
              'get_result_traceback_display', 'celery_task_id', 'tags',
              'created_by')
    readonly_fields = ('name', 'description', 'status', 'get_launch_job_display',
                       'get_result_stdout_display', 'get_result_stderr_display',
                       'get_result_traceback_display', 'celery_task_id',
                       'created_by', 'tags', 'audit_trail', 'active')
    filter_horizontal = ('tags',)
    inlines = [LaunchJobHostSummaryInlineForLaunchJobStatus,
               LaunchJobStatusEventInlineForLaunchJobStatus]

    def has_add_permission(self, request):
        return False

    def get_launch_job_display(self, obj):
        info = obj.launch_job._meta.app_label, obj.launch_job._meta.module_name
        lj_url = reverse('admin:%s_%s_change' % info, args=(obj.launch_job.pk,),
                         current_app=self.admin_site.name)
        return format_html('<a href="{0}">{1}</a>', lj_url, obj.launch_job)
    get_launch_job_display.short_description = _('Launch job')
    get_launch_job_display.allow_tags = True

    def get_result_stdout_display(self, obj):
        return format_html('<pre class="result-display">{0}</pre>', obj.result_stdout or ' ')
    get_result_stdout_display.short_description = _('Stdout')
    get_result_stdout_display.allow_tags = True

    def get_result_stderr_display(self, obj):
        return format_html('<pre class="result-display">{0}</pre>', obj.result_stderr or ' ')
    get_result_stderr_display.short_description = _('Stderr')
    get_result_stderr_display.allow_tags = True

    def get_result_traceback_display(self, obj):
        return format_html('<pre class="result-display">{0}</pre>', obj.result_traceback or ' ')
    get_result_traceback_display.short_description = _('Traceback')
    get_result_traceback_display.allow_tags = True

# FIXME: Add the rest of the models...

admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Inventory, InventoryAdmin)
admin.site.register(Tag, TagAdmin)
#admin.site.register(AuditTrail, AuditTrailAdmin)
admin.site.register(Host, HostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(VariableData, VariableDataAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Credential, CredentialAdmin)
admin.site.register(LaunchJob, LaunchJobAdmin)
admin.site.register(LaunchJobStatus, LaunchJobStatusAdmin)
