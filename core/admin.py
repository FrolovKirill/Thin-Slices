from django.contrib import admin
from .models import Project, Sample, AnalysisResult

admin.site.register(Project)
admin.site.register(Sample)
admin.site.register(AnalysisResult)