from __future__ import absolute_import

import json
import mock

from django.core.urlresolvers import reverse

from sentry.models import (
    ExternalIssue, Integration, IntegrationExternalProject, OrganizationIntegration
)
from sentry.testutils import APITestCase
from sentry.utils.http import absolute_uri


SAMPLE_CREATE_META_RESPONSE = """
{
  "projects": [
    {
      "self": "http://www.example.com/jira/rest/api/2/project/EX",
      "id": "10000",
      "key": "EX",
      "name": "Example Project",
      "avatarUrls": {
        "48x48": "http://www.example.com/jira/secure/projectavatar?pid=10000&avatarId=10011",
        "24x24": "http://www.example.com/jira/secure/projectavatar?size=small&pid=10000&avatarId=10011",
        "16x16": "http://www.example.com/jira/secure/projectavatar?size=xsmall&pid=10000&avatarId=10011",
        "32x32": "http://www.example.com/jira/secure/projectavatar?size=medium&pid=10000&avatarId=10011"
      },
      "issuetypes": [
        {
          "self": "http://www.example.com/jira/rest/api/2/issueType/1",
          "id": "1",
          "description": "An error in the code",
          "iconUrl": "http://www.example.com/jira/images/icons/issuetypes/bug.png",
          "name": "Bug",
          "subtask": false,
          "fields": {
            "issuetype": {
              "required": true,
              "name": "Issue Type",
              "key": "issuetype",
              "hasDefaultValue": false,
              "operations": [
                "set"
              ]
            }
          }
        }
      ]
    }
  ]
}
"""

SAMPLE_PROJECT_LIST_RESPONSE = """
[
  {
    "self": "http://www.example.com/jira/rest/api/2/project/EX",
    "id": "10000",
    "key": "EX",
    "name": "Example",
    "avatarUrls": {
      "48x48": "http://www.example.com/jira/secure/projectavatar?size=large&pid=10000",
      "24x24": "http://www.example.com/jira/secure/projectavatar?size=small&pid=10000",
      "16x16": "http://www.example.com/jira/secure/projectavatar?size=xsmall&pid=10000",
      "32x32": "http://www.example.com/jira/secure/projectavatar?size=medium&pid=10000"
    },
    "projectCategory": {
      "self": "http://www.example.com/jira/rest/api/2/projectCategory/10000",
      "id": "10000",
      "name": "FIRST",
      "description": "First Project Category"
    },
    "simplified": false
  },
  {
    "self": "http://www.example.com/jira/rest/api/2/project/ABC",
    "id": "10001",
    "key": "ABC",
    "name": "Alphabetical",
    "avatarUrls": {
      "48x48": "http://www.example.com/jira/secure/projectavatar?size=large&pid=10001",
      "24x24": "http://www.example.com/jira/secure/projectavatar?size=small&pid=10001",
      "16x16": "http://www.example.com/jira/secure/projectavatar?size=xsmall&pid=10001",
      "32x32": "http://www.example.com/jira/secure/projectavatar?size=medium&pid=10001"
    },
    "projectCategory": {
      "self": "http://www.example.com/jira/rest/api/2/projectCategory/10000",
      "id": "10000",
      "name": "FIRST",
      "description": "First Project Category"
    },
    "simplified": false
  }
]
"""

SAMPLE_GET_ISSUE_RESPONSE = """
{
    "expand": "renderedFields,names,schema,operations,editmeta,changelog,versionedRepresentations",
    "fields": {
        "aggregateprogress": {
            "progress": 0,
            "total": 0
        },
        "aggregatetimeestimate": null,
        "aggregatetimeoriginalestimate": null,
        "aggregatetimespent": null,
        "assignee": null,
        "attachment": [],
        "comment": {
            "comments": [],
            "maxResults": 0,
            "startAt": 0,
            "total": 0
        },
        "components": [],
        "created": "2018-06-15T11:47:57.111-0700",
        "creator": {
            "accountId": "5ada5260ba41192e23d7c924",
            "active": true,
            "avatarUrls": {
                "16x16": "https://avatar-cdn.atlassian.com/a2f1a9a289088349aecc98a4fc6eff2b?s=16&d=https%3A%2F%2Fsecure.gravatar.com%2Favatar%2Fa2f1a9a289088349aecc98a4fc6eff2b%3Fd%3Dmm%26s%3D16%26noRedirect%3Dtrue",
                "24x24": "https://avatar-cdn.atlassian.com/a2f1a9a289088349aecc98a4fc6eff2b?s=24&d=https%3A%2F%2Fsecure.gravatar.com%2Favatar%2Fa2f1a9a289088349aecc98a4fc6eff2b%3Fd%3Dmm%26s%3D24%26noRedirect%3Dtrue",
                "32x32": "https://avatar-cdn.atlassian.com/a2f1a9a289088349aecc98a4fc6eff2b?s=32&d=https%3A%2F%2Fsecure.gravatar.com%2Favatar%2Fa2f1a9a289088349aecc98a4fc6eff2b%3Fd%3Dmm%26s%3D32%26noRedirect%3Dtrue",
                "48x48": "https://avatar-cdn.atlassian.com/a2f1a9a289088349aecc98a4fc6eff2b?s=48&d=https%3A%2F%2Fsecure.gravatar.com%2Favatar%2Fa2f1a9a289088349aecc98a4fc6eff2b%3Fd%3Dmm%26s%3D48%26noRedirect%3Dtrue"
            },
            "displayName": "Sentry",
            "emailAddress": "example.io.jira@connect.atlassian.com",
            "key": "addon_example.io.jira",
            "name": "addon_example.io.jira",
            "self": "https://getsentry-dev.atlassian.net/rest/api/2/user?username=addon_example.io.jira",
            "timeZone": "America/Los_Angeles"
        },
        "customfield_10000": null,
        "customfield_10001": null,
        "customfield_10002": null,
        "customfield_10006": [],
        "customfield_10007": "0|i000b3:",
        "customfield_10008": null,
        "customfield_10009": [],
        "customfield_10010": null,
        "customfield_10011": null,
        "customfield_10012": null,
        "customfield_10026": null,
        "customfield_10027": null,
        "customfield_10028": null,
        "customfield_10100": null,
        "customfield_10200": "{}",
        "customfield_10400": null,
        "customfield_10500": null,
        "customfield_10600": null,
        "customfield_10601": null,
        "customfield_10602": null,
        "customfield_10603": null,
        "customfield_10604": null,
        "customfield_10605": null,
        "customfield_10701": null,
        "customfield_10702": null,
        "description": "example bug report",
        "duedate": null,
        "environment": null,
        "fixVersions": [],
        "issuelinks": [],
        "issuetype": {
            "avatarId": 10318,
            "description": "A task that needs to be done.",
            "iconUrl": "https://getsentry-dev.atlassian.net/secure/viewavatar?size=xsmall&avatarId=10318&avatarType=issuetype",
            "id": "10200",
            "name": "Task",
            "self": "https://getsentry-dev.atlassian.net/rest/api/2/issuetype/10200",
            "subtask": false
        },
        "labels": [],
        "lastViewed": null,
        "priority": {
            "iconUrl": "https://getsentry-dev.atlassian.net/images/icons/priorities/medium.svg",
            "id": "3",
            "name": "Medium",
            "self": "https://getsentry-dev.atlassian.net/rest/api/2/priority/3"
        },
        "progress": {
            "progress": 0,
            "total": 0
        },
        "project": {
            "avatarUrls": {
                "16x16": "https://getsentry-dev.atlassian.net/secure/projectavatar?size=xsmall&avatarId=10324",
                "24x24": "https://getsentry-dev.atlassian.net/secure/projectavatar?size=small&avatarId=10324",
                "32x32": "https://getsentry-dev.atlassian.net/secure/projectavatar?size=medium&avatarId=10324",
                "48x48": "https://getsentry-dev.atlassian.net/secure/projectavatar?avatarId=10324"
            },
            "id": "10100",
            "key": "SEN",
            "name": "sentry",
            "projectTypeKey": "software",
            "self": "https://getsentry-dev.atlassian.net/rest/api/2/project/10100"
        },
        "reporter": {
            "accountId": "557058:2b9b2878-fb9d-48b2-a166-86c179604206",
            "active": true,
            "avatarUrls": {
                "16x16": "https://avatar-cdn.atlassian.com/d8bd4a393e73ee8e17b54afba66af5e8?s=16&d=https%3A%2F%2Fsecure.gravatar.com%2Favatar%2Fd8bd4a393e73ee8e17b54afba66af5e8%3Fd%3Dmm%26s%3D16%26noRedirect%3Dtrue",
                "24x24": "https://avatar-cdn.atlassian.com/d8bd4a393e73ee8e17b54afba66af5e8?s=24&d=https%3A%2F%2Fsecure.gravatar.com%2Favatar%2Fd8bd4a393e73ee8e17b54afba66af5e8%3Fd%3Dmm%26s%3D24%26noRedirect%3Dtrue",
                "32x32": "https://avatar-cdn.atlassian.com/d8bd4a393e73ee8e17b54afba66af5e8?s=32&d=https%3A%2F%2Fsecure.gravatar.com%2Favatar%2Fd8bd4a393e73ee8e17b54afba66af5e8%3Fd%3Dmm%26s%3D32%26noRedirect%3Dtrue",
                "48x48": "https://avatar-cdn.atlassian.com/d8bd4a393e73ee8e17b54afba66af5e8?s=48&d=https%3A%2F%2Fsecure.gravatar.com%2Favatar%2Fd8bd4a393e73ee8e17b54afba66af5e8%3Fd%3Dmm%26s%3D48%26noRedirect%3Dtrue"
            },
            "displayName": "Jess MacQueen",
            "emailAddress": "jess@sentry.io",
            "key": "admin",
            "name": "admin",
            "self": "https://getsentry-dev.atlassian.net/rest/api/2/user?username=admin",
            "timeZone": "America/Los_Angeles"
        },
        "resolution": null,
        "resolutiondate": null,
        "security": null,
        "status": {
            "description": "",
            "iconUrl": "https://getsentry-dev.atlassian.net/",
            "id": "10100",
            "name": "To Do",
            "self": "https://getsentry-dev.atlassian.net/rest/api/2/status/10100",
            "statusCategory": {
                "colorName": "blue-gray",
                "id": 2,
                "key": "new",
                "name": "To Do",
                "self": "https://getsentry-dev.atlassian.net/rest/api/2/statuscategory/2"
            }
        },
        "subtasks": [],
        "summary": "example summary",
        "timeestimate": null,
        "timeoriginalestimate": null,
        "timespent": null,
        "timetracking": {},
        "updated": "2018-06-28T14:12:29.014-0700",
        "versions": [],
        "votes": {
            "hasVoted": false,
            "self": "https://getsentry-dev.atlassian.net/rest/api/2/issue/SEN-5/votes",
            "votes": 0
        },
        "watches": {
            "isWatching": true,
            "self": "https://getsentry-dev.atlassian.net/rest/api/2/issue/SEN-5/watchers",
            "watchCount": 1
        },
        "worklog": {
            "maxResults": 20,
            "startAt": 0,
            "total": 0,
            "worklogs": []
        },
        "workratio": -1
    },
    "id": "10305",
    "key": "SEN-5",
    "self": "https://getsentry-dev.atlassian.net/rest/api/2/issue/10305"
}
"""

SAMPLE_TRANSITION_RESPONSE = """
{
    "expand": "transitions",
    "transitions": [
        {
            "hasScreen": false,
            "id": "11",
            "isConditional": false,
            "isGlobal": true,
            "isInitial": false,
            "name": "To Do",
            "to": {
                "description": "",
                "iconUrl": "https://getsentry-dev.atlassian.net/",
                "id": "10100",
                "name": "To Do",
                "self": "https://getsentry-dev.atlassian.net/rest/api/2/status/10100",
                "statusCategory": {
                    "colorName": "blue-gray",
                    "id": 2,
                    "key": "new",
                    "name": "To Do",
                    "self": "https://getsentry-dev.atlassian.net/rest/api/2/statuscategory/2"
                }
            }
        },
        {
            "hasScreen": false,
            "id": "21",
            "isConditional": false,
            "isGlobal": true,
            "isInitial": false,
            "name": "In Progress",
            "to": {
                "description": "This issue is being actively worked on at the moment by the assignee.",
                "iconUrl": "https://getsentry-dev.atlassian.net/images/icons/statuses/inprogress.png",
                "id": "3",
                "name": "In Progress",
                "self": "https://getsentry-dev.atlassian.net/rest/api/2/status/3",
                "statusCategory": {
                    "colorName": "yellow",
                    "id": 4,
                    "key": "indeterminate",
                    "name": "In Progress",
                    "self": "https://getsentry-dev.atlassian.net/rest/api/2/statuscategory/4"
                }
            }
        },
        {
            "hasScreen": false,
            "id": "31",
            "isConditional": false,
            "isGlobal": true,
            "isInitial": false,
            "name": "Done",
            "to": {
                "description": "",
                "iconUrl": "https://getsentry-dev.atlassian.net/",
                "id": "10101",
                "name": "Done",
                "self": "https://getsentry-dev.atlassian.net/rest/api/2/status/10101",
                "statusCategory": {
                    "colorName": "green",
                    "id": 3,
                    "key": "done",
                    "name": "Done",
                    "self": "https://getsentry-dev.atlassian.net/rest/api/2/statuscategory/3"
                }
            }
        }
    ]
}
"""


class MockJiraApiClient(object):
    def get_create_meta(self, project=None):
        return json.loads(SAMPLE_CREATE_META_RESPONSE)

    def get_create_meta_for_project(self, project):
        return self.get_create_meta()['projects'][0]

    def get_projects_list(self):
        return json.loads(SAMPLE_PROJECT_LIST_RESPONSE)

    def get_issue(self, issue_key):
        return json.loads(SAMPLE_GET_ISSUE_RESPONSE.strip())

    def create_issue(self, data):
        return {'key': 'APP-123'}

    def get_transitions(self, issue_key):
        return json.loads(SAMPLE_TRANSITION_RESPONSE)['transitions']

    def transition_issue(self, issue_key, transition_id):
        pass


class JiraIntegrationTest(APITestCase):
    def test_get_create_issue_config(self):
        org = self.organization
        self.login_as(self.user)
        group = self.create_group()
        self.create_event(group=group)

        integration = Integration.objects.create(
            provider='jira',
            name='Example Jira',
        )
        integration.add_organization(org.id)

        installation = integration.get_installation(org.id)

        def get_client():
            return MockJiraApiClient()

        with mock.patch.object(installation, 'get_client', get_client):
            assert installation.get_create_issue_config(group) == [{
                'default': '10000',
                'choices': [('10000', 'EX'), ('10001', 'ABC')],
                'type': 'select',
                'name': 'project',
                'label': 'Jira Project',
                'updatesForm': True,
            }, {
                'default': 'message',
                'type': 'string',
                'name': 'title',
                'label': 'Title',
                'required': True,
            }, {
                'default': ('%s\n\n{code}\n'
                            'Stacktrace (most recent call last):\n\n  '
                            'File "sentry/models/foo.py", line 29, in build_msg\n    '
                            'string_max_length=self.string_max_length)\n\nmessage\n{code}'
                            ) % (absolute_uri(group.get_absolute_url()),),
                'type': 'textarea',
                'name': 'description',
                'label': 'Description',
                'autosize': True,
                'maxRows': 10,
            }, {
                'default': '1',
                'choices': [('1', 'Bug')],
                'type': 'select',
                'name': 'issuetype',
                'label': 'Issue Type',
                'updatesForm': True,
            }]

    def test_get_link_issue_config(self):
        org = self.organization
        self.login_as(self.user)
        group = self.create_group()

        integration = Integration.objects.create(
            provider='jira',
            name='Example Jira',
        )
        integration.add_organization(org.id)

        installation = integration.get_installation(org.id)

        assert installation.get_link_issue_config(group) == [
            {
                'name': 'externalIssue',
                'label': 'Issue',
                'default': '',
                'type': 'select',
                'url': reverse(
                    'sentry-extensions-jira-search', args=[org.slug, integration.id],
                )
            }
        ]

    def test_create_issue(self):
        org = self.organization
        self.login_as(self.user)

        integration = Integration.objects.create(
            provider='jira',
            name='Example Jira',
        )
        integration.add_organization(org.id)

        installation = integration.get_installation(org.id)

        def get_client():
            return MockJiraApiClient()

        with mock.patch.object(installation, 'get_client', get_client):
            assert installation.create_issue({
                'title': 'example summary',
                'description': 'example bug report',
                'issuetype': '1',
                'project': '10000',
            }) == {
                'title': 'example summary',
                'description': 'example bug report',
                'key': 'APP-123'
            }

    def test_outbound_issue_sync(self):
        org = self.organization
        project = self.project
        self.login_as(self.user)

        integration = Integration.objects.create(
            provider='jira',
            name='Example Jira',
        )
        integration.add_organization(org.id)

        external_issue = ExternalIssue.objects.create(
            organization_id=org.id,
            integration_id=integration.id,
            key='SEN-5',
        )

        IntegrationExternalProject.objects.create(
            external_id="10100",
            organization_integration_id=OrganizationIntegration.objects.get(
                organization_id=org.id,
                integration_id=integration.id,
            ).id,
            resolved_status="10101",
            unresolved_status="3",
        )

        installation = integration.get_installation(org.id)

        with mock.patch.object(MockJiraApiClient, 'transition_issue') as mock_transition_issue:
            def get_client():
                return MockJiraApiClient()

            with mock.patch.object(installation, 'get_client', get_client):
                # test unresolve -- 21 is "in progress" transition id
                installation.sync_status_outbound(external_issue, False, project.id)
                mock_transition_issue.assert_called_with('SEN-5', '21')

                # test resolve -- 31 is "done" transition id
                installation.sync_status_outbound(external_issue, True, project.id)
                mock_transition_issue.assert_called_with('SEN-5', '31')

    def test_update_organization_config(self):
        org = self.organization
        self.login_as(self.user)

        integration = Integration.objects.create(
            provider='jira',
            name='Example Jira',
        )
        integration.add_organization(org.id)

        installation = integration.get_installation(org.id)

        data = {
            'sync_comments': True,
            'sync_forward_assignment': True,
            'sync_reverse_assignment': True,
            'sync_status_reverse': True,
            'sync_status_forward': {
                10100: {
                    'on_resolve': '4',
                    'on_unresolve': '3',
                },
            },
        }

        installation.update_organization_config(data)

        org_integration = OrganizationIntegration.objects.get(
            organization_id=org.id,
            integration_id=integration.id,
        )

        assert org_integration.config == {
            'sync_comments': True,
            'sync_forward_assignment': True,
            'sync_reverse_assignment': True,
            'sync_status_reverse': True,
            'sync_status_forward': True,
        }

        assert IntegrationExternalProject.objects.filter(
            organization_integration_id=org_integration.id,
            resolved_status='4',
            unresolved_status='3',
        ).exists()

        # test update existing
        data = {
            'sync_comments': True,
            'sync_forward_assignment': True,
            'sync_reverse_assignment': True,
            'sync_status_reverse': True,
            'sync_status_forward': {
                10100: {
                    'on_resolve': '4',
                    'on_unresolve': '5',
                },
            },
        }

        installation.update_organization_config(data)

        org_integration = OrganizationIntegration.objects.get(
            organization_id=org.id,
            integration_id=integration.id,
        )

        assert org_integration.config == {
            'sync_comments': True,
            'sync_forward_assignment': True,
            'sync_reverse_assignment': True,
            'sync_status_reverse': True,
            'sync_status_forward': True,
        }

        assert IntegrationExternalProject.objects.filter(
            organization_integration_id=org_integration.id,
            resolved_status='4',
            unresolved_status='5',
        ).exists()

        assert IntegrationExternalProject.objects.filter(
            organization_integration_id=org_integration.id,
        ).count() == 1

        # test disable forward
        data = {
            'sync_comments': True,
            'sync_forward_assignment': True,
            'sync_reverse_assignment': True,
            'sync_status_reverse': True,
            'sync_status_forward': {},
        }

        installation.update_organization_config(data)

        org_integration = OrganizationIntegration.objects.get(
            organization_id=org.id,
            integration_id=integration.id,
        )

        assert org_integration.config == {
            'sync_comments': True,
            'sync_forward_assignment': True,
            'sync_reverse_assignment': True,
            'sync_status_reverse': True,
            'sync_status_forward': False,
        }

        assert IntegrationExternalProject.objects.filter(
            organization_integration_id=org_integration.id,
        ).count() == 0

    def test_get_config_data(self):
        org = self.organization
        self.login_as(self.user)

        integration = Integration.objects.create(
            provider='jira',
            name='Example Jira',
        )
        integration.add_organization(org.id)

        org_integration = OrganizationIntegration.objects.get(
            organization_id=org.id,
            integration_id=integration.id,
        )

        org_integration.config = {
            'sync_comments': True,
            'sync_forward_assignment': True,
            'sync_reverse_assignment': True,
            'sync_status_reverse': True,
            'sync_status_forward': True,
        }
        org_integration.save()

        IntegrationExternalProject.objects.create(
            organization_integration_id=org_integration.id,
            external_id='12345',
            unresolved_status='in_progress',
            resolved_status='done',
        )

        installation = integration.get_installation(org.id)

        assert installation.get_config_data() == {
            'sync_comments': True,
            'sync_forward_assignment': True,
            'sync_reverse_assignment': True,
            'sync_status_reverse': True,
            'sync_status_forward': {
                '12345': {
                    'on_resolve': 'done',
                    'on_unresolve': 'in_progress',
                },
            },
        }
