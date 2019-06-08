from django.db import models

# Create your models here.
photo = models.ImageField(upload_to="gallery")

class Students(models.Model):
    student_id = models.IntegerField()
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    discipline = models.CharField(max_length=200)
    year = models.CharField(max_length=200)
    phone = models.IntegerField(default=0)
    interview_offer = models.BooleanField(null=True, default=None)
    project_name = models.CharField(max_length=200)

class Teams(models.Model):
    team_name = models.CharField(max_length=200)
    num_members = models.IntegerField()
    avg_yos = models.FloatField()
    most_common_discipline = models.CharField(max_length=200)


class Projects(models.Model):
    project_name = models.CharField(max_length=200)
    client_name = models.CharField(max_length=200)
    completion_rate = models.FloatField(max_length=200)
    project_type = models.CharField(max_length=200)


class NotForProfits(models.Model):
    nfp_name = models.CharField(max_length=200)
    years_w_veep = models.FloatField()
    num_projects = models.IntegerField()
    num_projects_completed = models.IntegerField()
    primary_email = models.CharField(max_length=200)

