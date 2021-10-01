from django.test import TestCase
from django.contrib.auth import get_user_model
from account.models import Profile
from .models import Project, Issue, Log, TimeEntry
from django.utils import timezone
from datetime import timedelta


User = get_user_model()


class TrackerTestUtils(TestCase):
    def create_users(self, usernames):
        """
        Create generic users using passed usernames and commit them to a database.
        """
        for username in usernames:
            user = User(username=username, email=f"{username}@example.com")
            user.set_password("123")
            profile = Profile(user=user)
            user.profile = profile
            user.save()
            profile.save()

    def create_projects(self, projects):
        """
        Create generic projects using passed iterable object of kwargs and project
        members and commit them to a database.
        """
        for kwargs, members in projects:
            project = Project.objects.create(**kwargs)
            member_pks = [
                User.objects.get(username=username).pk for username in members
            ]
            project.members.set(member_pks)

    def create_issues(self, issues):
        """
        Create generic issues using passed iterable object of kwargs and related
        object pks and commit them to a database.
        """
        for kwargs, creator_name, assignee_name, project_name, tasks in issues:
            issue = Issue.objects.create(
                **kwargs,
                creator=User.objects.get(username=creator_name),
                assignee=User.objects.get(username=assignee_name),
                project=Project.objects.get(name=project_name),
            )
            child_task_pks = [Issue.objects.get(name=name).pk for name in tasks]
            issue.child_tasks.set(child_task_pks)

    def setUp(self):
        self.create_users(f"tester{i}" for i in range(4))

        projects = [
            (
                {"name": "project0", "creator": User.objects.get(username="tester0")},
                ("tester2",),
            ),
            (
                {"name": "project1", "creator": User.objects.get(username="tester0")},
                ("tester2", "tester3"),
            ),
            (
                {"name": "project2", "creator": User.objects.get(username="tester1")},
                ("tester0", "tester3"),
            ),
        ]
        self.create_projects(projects)

        issues = [
            (
                {
                    "name": "issue0",
                    "description": "...",
                    "issue_type": "top",
                    "status": "in_progress",
                    "work_effort_estimate": 5,
                    "due_date": timezone.now() + timedelta(days=2),
                },
                "tester2",  # creator
                "tester2",  # assignee
                "project0",
                [],
            ),
            (
                {
                    "name": "issue1",
                    "description": "...",
                    "issue_type": "low",
                    "status": "done",
                    "work_effort_estimate": 3,
                    "due_date": timezone.now() + timedelta(days=5),
                },
                "tester2",  # creator
                "tester0",  # assignee
                "project0",
                ["issue0"],
            ),
            (
                {
                    "name": "issue2",
                    "description": "...",
                    "issue_type": "high",
                    "status": "in_review",
                    "work_effort_estimate": 22,
                    "due_date": timezone.now() - timedelta(days=7),
                },
                "tester3",  # creator
                "tester0",  # assignee
                "project2",
                ["issue0", "issue1"],
            ),
            (
                {
                    "name": "issue3",
                    "description": "...",
                    "issue_type": "high",
                    "status": "in_review",
                    "work_effort_estimate": 22,
                    "due_date": timezone.now() - timedelta(days=7),
                },
                "tester1",  # creator
                "tester3",  # assignee
                "project2",
                [],
            ),
        ]
        self.create_issues(issues)


# Tests
class ProjectIssueTestCase(TrackerTestUtils):
    def test_project_open_issues(self):
        """
        The count of open issues for a project should match the number of issue
        objects that are not in 'done' status and are linked to that project.
        """
        self.assertEqual(Project.objects.get(name="project0").open_issues, 1)
        self.assertEqual(Project.objects.get(name="project2").open_issues, 2)

    def test_project_closed_issues(self):
        """
        The count of closed issues for a project should match the number of issue
        objects that are in 'done' status and are linked to that project.
        """
        self.assertEqual(Project.objects.get(name="project0").closed_issues, 1)
        self.assertEqual(Project.objects.get(name="project2").closed_issues, 0)

    def test_issue_view_permission(self):
        """
        Only members and a leader of a project should have 'view_project'
        permission to a specific project instance.
        """
        self.assertIs(
            User.objects.get(username="tester2").has_perm(
                "view_project", Project.objects.get(name="project1")
            ),
            True,
        )
        self.assertIs(
            User.objects.get(username="tester0").has_perm(
                "view_project", Project.objects.get(name="project0")
            ),
            True,
        )
        self.assertIs(
            User.objects.get(username="tester1").has_perm(
                "view_project", Project.objects.get(name="project1")
            ),
            False,
        )

    def test_issue_change_permission(self):
        """
        Only members and a leader of a project should have 'change_project_issue'
        permission to a specific project instance.
        """
        self.assertIs(
            User.objects.get(username="tester0").has_perm(
                "change_project_issue", Project.objects.get(name="project0")
            ),
            True,
        )
        self.assertIs(
            User.objects.get(username="tester2").has_perm(
                "change_project_issue", Project.objects.get(name="project0")
            ),
            True,
        )
        self.assertIs(
            User.objects.get(username="tester3").has_perm(
                "change_project_issue", Project.objects.get(name="project0")
            ),
            False,
        )

    def test_issue_delete_permission(self):
        """
        Only issue creator and a leader of a project should have 'delete_issue'
        permission to a specific issue instance.
        """
        self.assertIs(
            User.objects.get(username="tester3").has_perm(
                "delete_issue", Issue.objects.get(name="issue2")
            ),
            True,
        )
        self.assertIs(
            User.objects.get(username="tester1").has_perm(
                "delete_issue", Issue.objects.get(name="issue2")
            ),
            True,
        )
        self.assertIs(
            User.objects.get(username="tester0").has_perm(
                "delete_issue", Issue.objects.get(name="issue2")
            ),
            False,
        )
        self.assertIs(
            User.objects.get(username="tester2").has_perm(
                "delete_issue", Issue.objects.get(name="issue2")
            ),
            False,
        )

    def test_project_change_delete_permission(self):
        """
        Only leader of a project should have 'change_project'
        and 'delete_project' permissions to a specific project instance.
        """
        self.assertIs(
            User.objects.get(username="tester0").has_perm(
                "change_project", Project.objects.get(name="project0")
            ),
            True,
        )
        self.assertIs(
            User.objects.get(username="tester2").has_perm(
                "change_project", Project.objects.get(name="project0")
            ),
            False,
        )
        self.assertIs(
            User.objects.get(username="tester1").has_perm(
                "delete_project", Project.objects.get(name="project2")
            ),
            True,
        )
        self.assertIs(
            User.objects.get(username="tester3").has_perm(
                "delete_project", Project.objects.get(name="project2")
            ),
            False,
        )


class TimeEntryTestCase(TrackerTestUtils):
    def test_project_work_effort_actual(self):
        """
        Work effort should be logged and calculated correctly for projects.
        """
        TimeEntry.objects.create(
            user=User.objects.get(username="tester0"),
            issue=Issue.objects.get(name="issue3"),
            end_time=timezone.now() + timedelta(hours=2),
        )
        TimeEntry.objects.create(
            user=User.objects.get(username="tester3"),
            issue=Issue.objects.get(name="issue2"),
            end_time=timezone.now() + timedelta(hours=2),
        )
        self.assertAlmostEqual(
            Project.objects.get(name="project2").work_effort_actual, 240
        )

    def test_issue_work_effort_actual(self):
        """
        Work effort should be logged and calculated correctly for issues.
        """
        TimeEntry.objects.create(
            user=User.objects.get(username="tester0"),
            issue=Issue.objects.get(name="issue3"),
            end_time=timezone.now() + timedelta(hours=2),
        )
        TimeEntry.objects.create(
            user=User.objects.get(username="tester3"),
            issue=Issue.objects.get(name="issue3"),
            end_time=timezone.now() + timedelta(hours=1),
        )
        self.assertAlmostEqual(
            Issue.objects.get(name="issue3").work_effort_actual, 180
        )

    def test_time_entry_is_active(self):
        """
        Time entry object without an end date should appear as active.
        """
        te = TimeEntry.objects.create(
            user=User.objects.get(username="tester0"),
            issue=Issue.objects.get(name="issue3"),
        )
        self.assertEqual(te.is_active, True)
        te.end_time = timezone.now()
        self.assertEqual(te.is_active, False)


class LogTestCase(TrackerTestUtils):
    def test_user_project_creation_log(self):
        """
        The count of logged project creations should match the number of projects
        created by a queried user.
        """
        self.assertEqual(
            User.objects.get(username="tester0").logs.filter(issue=None).count(), 2
        )
        self.assertEqual(
            User.objects.get(username="tester1").logs.filter(issue=None).count(), 1
        )
        self.assertEqual(
            User.objects.get(username="tester2").logs.filter(issue=None).count(), 0
        )

    def test_user_issue_creation_log(self):
        """
        The count of logged issue creations should match the number of issues
        created by a queried user.
        """
        self.assertEqual(
            User.objects.get(username="tester2").logs.exclude(issue=None).count(), 2
        )
        self.assertEqual(
            User.objects.get(username="tester0").logs.exclude(issue=None).count(), 0
        )

    def test_user_project_change_log(self):
        """
        Update to a project object is properly logged.
        """
        project = Project.objects.get(name="project2")
        user = User.objects.get(username="tester1")
        log_count = user.logs.filter(project=project).count()
        project.name = "project20"
        project.last_update_by = user
        project.save()
        self.assertEqual(user.logs.filter(project=project).count(), log_count + 1)

    def test_user_issue_change_log(self):
        """
        Update to an issue object is properly logged.
        """
        issue = Issue.objects.get(name="issue2")
        user = User.objects.get(username="tester0")
        log_count = user.logs.filter(issue=issue).count()
        issue.name = "issue20"
        issue.last_update_by = user
        issue.save()
        self.assertEqual(user.logs.filter(issue=issue).count(), log_count + 1)

    def test_project_delete_log(self):
        """
        Deletion of a project is properly logged.
        """
        project = Project.objects.get(name="project2")
        user = User.objects.get(username="tester1")
        log_count = user.logs.filter(project=project).exclude(removed_object="").count()
        project.last_update_by = user
        project.delete()
        self.assertEqual(
            user.logs.filter(project=project).exclude(removed_object="").count(),
            log_count + 1,
        )

    def test_issue_delete_log(self):
        """
        Deletion of an issue is properly logged.
        """
        issue = Issue.objects.get(name="issue2")
        user = User.objects.get(username="tester0")
        log_count = user.logs.filter(issue=issue).exclude(removed_object="").count()
        issue.last_update_by = user
        issue.delete()
        self.assertEqual(
            user.logs.filter(issue=issue).exclude(removed_object="").count(),
            log_count + 1,
        )
