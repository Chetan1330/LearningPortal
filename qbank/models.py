from django.db import models
from datetime import datetime   
# Create your models here.
from django.urls import reverse
from django.contrib.auth.models import User


class Category(models.Model):
    category_id = models.BigAutoField(primary_key=True)
    category_name = models.CharField(max_length=200, blank=True, null=True)
    description = models.CharField(max_length=300, blank=True, null=True)

    def __str__(self):
        return '' + self.category_name
    class Meta:
        managed = True
        db_table = 'Category'

class ExamHeader(models.Model):
    exam_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    desc = models.TextField( blank=True, null=True)
    keywords = models.CharField(max_length=300, blank=True, null=True)
    slug = models.CharField(max_length=300, blank=True, null=True)
    duration_m = models.IntegerField(blank=True, null=True)
    category_ref = models.ForeignKey(Category, models.DO_NOTHING, blank=True, null=True)
    date = models.DateTimeField(default=datetime.now, blank=True)
    pass_score = models.IntegerField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse('exam', args=[str(self.slug)])

    def __str__(self):
        return '' + self.name    

    class Meta:
        managed = True
        db_table = 'ExamHeader'


class ExamQuestion(models.Model):
    question_id = models.BigAutoField(primary_key=True)
    question_num = models.IntegerField(blank=True, null=True)
    question = models.TextField(blank=True, null=True)
    option_a = models.TextField(blank=True, null=True)
    option_b = models.TextField(blank=True, null=True)
    option_c = models.TextField(blank=True, null=True)
    option_d = models.TextField(blank=True, null=True)
    option_e = models.TextField(blank=True, null=True)
    option_f = models.TextField(blank=True, null=True)
    answer = models.CharField(max_length=1000, blank=True, null=True)
    referrence = models.CharField(max_length=1000, blank=True, null=True)
    explanation = models.CharField(max_length=1000, blank=True, null=True)
    page_num = models.IntegerField(blank=True, null=True)
    exam_ref = models.ForeignKey(ExamHeader, models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return '' + str(self.question_id)

    class Meta:
        managed = True
        db_table = 'ExamQuestion'

class Profile(models.Model):
    profile_id = models.BigAutoField(primary_key=True)
    phone = models.CharField(max_length=50,blank=True, null=True)
    bachelor_degree = models.CharField(max_length=50,blank=True, null=True)
    bachelor_yop = models.IntegerField(blank=True, null=True)
    master_degree = models.CharField(max_length=50,blank=True, null=True)
    master_yop = models.IntegerField(blank=True, null=True)
    specialization = models.CharField(max_length=50,blank=True, null=True)
    auth_user_id = models.IntegerField(blank=True, null=True)
    first_name = models.CharField(max_length=50,blank=True, null=True,default='')
    last_name = models.CharField(max_length=50,blank=True, null=True)
    email = models.CharField(max_length=100,blank=True, null=True)

    def __str__(self):
            return '' + str(self.profile_id)
        
        
    class Meta:
            managed = True
            db_table = 'Profile'


class Project(models.Model):
    project_id = models.BigAutoField(primary_key=True)
    project_title = models.CharField(max_length=100,blank=True, null=True)
    duration = models.CharField(max_length=100,blank=True, null=True)
    tech_stack = models.CharField(max_length=100,blank=True, null=True)
    project_description = models.CharField(max_length=400,blank=True, null=True)
    auth_user_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
            return '' + str(self.profile_id)
        
        
    class Meta:
            managed = True
            db_table = 'Project'


class Dashboard(models.Model):
    dashboard_id = models.BigAutoField(primary_key=True)
    auth_user_id = models.IntegerField(blank=True, null=True)
    course_id = models.ForeignKey(ExamHeader, models.DO_NOTHING, blank=True, null=True)
    score_taken = models.CharField(max_length=100,blank=True, null=True)
    date = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
            return '' + str(self.dashboard_id)
        
        
    class Meta:
            managed = True
            db_table = 'Dashboard'


