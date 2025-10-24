from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    class_distribution = models.JSONField(default=dict, blank=True, null=True)

    global_metrics2_hist = models.ImageField(upload_to="global_stats/", null=True, blank=True)
    global_diam_hist = models.ImageField(upload_to="global_stats/", null=True, blank=True)
    global_stats = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

class Sample(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="samples")
    file = models.FileField(upload_to="samples/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    class_label = models.IntegerField(null=True, blank=True)  # 0, 1 или 2

    def __str__(self):
        return f"Sample {self.id} from {self.project.name}"
    
class AnalysisResult(models.Model):
    sample = models.OneToOneField(Sample, on_delete=models.CASCADE, related_name="analysis")
    result_text = models.TextField(blank=True, null=True)

    # Числовые метрики
    metric_1 = models.FloatField(blank=True, null=True)
    metric_2 = models.FloatField(blank=True, null=True)
    diameters = models.JSONField(blank=True, null=True)

    # Гистограммы (сохраняем пути к картинкам)
    histogram_1 = models.ImageField(upload_to="analysis/", blank=True, null=True)
    # histogram_2 = models.ImageField(upload_to="analysis/", blank=True, null=True)

    # Визуализации
    overlay = models.ImageField(upload_to="analysis/", blank=True, null=True)
