import django_filters
from data_display.models import Students, Teams, Projects, NotForProfits

class StudentFilter(django_filters.FilterSet):
    class Meta:
        model = Student
        fields = ('discipline', 'email', 'id', 'interview-offer', 'name', 'phone', 'project_name', 'student_id', 'year'
                                                                                                                 '')
class TeamFilter(django_filters.FilterSet):
    class Meta:
        model = Teams
        fields = ('team_name', 'num_members', 'avg_yos', 'most_common_discipline')

class ProjectFilter(django_filters.FilterSet):
    class Meta:
        model = Projects
        fields = ('project_name', 'client_name', 'completion_rate', 'project_type')

class NotForProfitFilter(django_filters.FilterSet):
    class Meta:
        model = NotForProfits
        fields = ('nfp_name', 'years_w_veep', 'num_projects', 'num_projects_completed', 'primary_email')
