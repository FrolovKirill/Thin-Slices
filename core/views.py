from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Project, Sample, AnalysisResult
from django import forms
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from model.my_model import classify_image, run_full_analysis
from django.contrib.auth import logout
import matplotlib.pyplot as plt
import io, base64
import numpy as np

def logout_view(request):
    logout(request)
    return redirect("login")

# форма для нового проекта
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name"]

@login_required
def dashboard(request):
    projects = Project.objects.filter(user=request.user)
    return render(request, "dashboard.html", {"projects": projects})


@login_required
def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            return redirect("dashboard")
    else:
        form = ProjectForm()
    return render(request, "create_project.html", {"form": form})


'''@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)

    # --- загрузка новых файлов ---
    if request.method == "POST" and request.FILES.getlist("files"):
        for f in request.FILES.getlist("files"):
            sample = Sample.objects.create(project=project, file=f)
            AnalysisResult.objects.create(sample=sample, result_text="Анализ пока не реализован")
        return redirect("project_detail", project_id=project.id)

    samples = project.samples.all()

    # --- собираем метрики и общие графики ---
    metrics_1, metrics_2 = [], []
    global_hist1, global_hist2 = None, None

    for sample in samples:
        if hasattr(sample, "analysis") and sample.analysis.metric_1 is not None:
            metrics_1.append(sample.analysis.metric_1)
            metrics_2.append(sample.analysis.metric_2)

            if not global_hist1 and sample.analysis.histogram_1:
                global_hist1 = sample.analysis.histogram_1
            if not global_hist2 and sample.analysis.histogram_2:
                global_hist2 = sample.analysis.histogram_2

    context = {
        "project": project,
        "samples": samples,
        "percentages": project.class_distribution or None,
        "global_hist1": global_hist1,
        "global_hist2": global_hist2,
        "mean_metric1": sum(metrics_1) / len(metrics_1) if metrics_1 else None,
        "mean_metric2": sum(metrics_2) / len(metrics_2) if metrics_2 else None,
    }

    return render(request, "project_detail.html", context)'''
    
@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)

    if request.method == "POST" and request.FILES.getlist("files"):
        for f in request.FILES.getlist("files"):
            sample = Sample.objects.create(project=project, file=f)
            AnalysisResult.objects.create(sample=sample, result_text="Анализ пока не реализован")
        return redirect("project_detail", project_id=project.id)

    samples = project.samples.all()
    stats = project.global_stats or {}

    context = {
        "project": project,
        "samples": samples,
        "percentages": project.class_distribution or None,
        "global_diam": stats.get("global_diam"),
        "mean_metric1": stats.get("mean_metric1"),
        "mean_metric2":stats.get("mean_metric2"),
        "metric2": stats.get("mean_metric2"),
    }

    return render(request, "project_detail.html", context)


@login_required
def classify_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)

    samples = project.samples.all()
    
    counts = {0: 0, 1: 0, 2: 0}
    for sample in samples:
        if sample.class_label is None:  # ⚡ только новые
            predicted_class = classify_image(sample.file.path)
            sample.class_label = predicted_class
            sample.save()
        counts[sample.class_label] += 1

    total = sum(counts.values())
    percentages = {cls: round(counts[cls] / total * 100, 2) if total > 0 else 0 for cls in counts}

    project.class_distribution = percentages
    project.save()

    # ⚡ редирект вместо render — сбрасываем форму и возвращаемся на detail
    return redirect("project_detail", project_id=project.id)


import matplotlib.pyplot as plt
import io
from django.core.files.base import ContentFile

'''@login_required
def full_analysis(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)

    samples = project.samples.filter(class_label=1)

    for sample in samples:
        if not hasattr(sample, "analysis") or sample.analysis.metric_1 is None:
            metric_1, metric_2, hist1_path, hist2_path, overlay_path = run_full_analysis(sample.file.path)

            analysis, created = AnalysisResult.objects.get_or_create(sample=sample)
            analysis.metric_1 = metric_1
            analysis.metric_2 = metric_2

            if hist1_path:
                with open(hist1_path, "rb") as f:
                    analysis.histogram_1.save(f"hist1_{sample.id}.png", ContentFile(f.read()), save=False)

            if hist2_path:
                with open(hist2_path, "rb") as f:
                    analysis.histogram_2.save(f"hist2_{sample.id}.png", ContentFile(f.read()), save=False)

            if overlay_path:
                with open(overlay_path, "rb") as f:
                    analysis.overlay.save(f"overlay_{sample.id}.png", ContentFile(f.read()), save=False)

            analysis.save()

    return redirect("project_detail", project_id=project.id)'''

'''@login_required
def full_analysis(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)

    samples = project.samples.filter(class_label=1)

    metrics_1, metrics_2 = [], []
    global_diam = []
    # global_hist1, global_hist2 = None, None

    for sample in samples:
        if not hasattr(sample, "analysis") or sample.analysis.metric_1 is None:
            # metric_1, metric_2, hist1_path, hist2_path, overlay_path = run_full_analysis(sample.file.path)
            metric_1, metric_2, hist1_path, overlay_path, diameters = run_full_analysis(sample.file.path)

            analysis, created = AnalysisResult.objects.get_or_create(sample=sample)
            analysis.metric_1 = metric_1
            analysis.metric_2 = metric_2

            if hist1_path:
                with open(hist1_path, "rb") as f:
                    analysis.histogram_1.save(f"hist1_{sample.id}.png", ContentFile(f.read()), save=False)

            if overlay_path:
                with open(overlay_path, "rb") as f:
                    analysis.overlay.save(f"overlay_{sample.id}.png", ContentFile(f.read()), save=False)

            analysis.save()

        # метрики собираем из базы (вдруг часть уже была)
        metrics_1.append(sample.analysis.metric_1)
        metrics_2.append(sample.analysis.metric_2)
        global_diam += diameters
        
    # обновляем общую инфу
    project.global_stats = {
        "mean_metric1": sum(metrics_1) / len(metrics_1) if metrics_1 else None,
        "metric2": metrics_2 if metrics_2 else None,
        "global_diam": global_diam if global_diam else None,
        # "global_hist2": global_hist2.url if global_hist2 else None,
    }
    project.save()

    return redirect("project_detail", project_id=project.id)'''

@login_required
def full_analysis(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)

    samples = project.samples.filter(class_label=1)

    metrics_1 = []
    metrics_2 = []
    global_diam = []

    # временные переменные для гистограмм
    hist_metrics2_buf = None
    hist_diam_buf = None

    for sample in samples:
        if not hasattr(sample, "analysis") or sample.analysis.metric_1 is None:
            metric_1, metric_2, hist1_path, overlay_path, diameters = run_full_analysis(sample.file.path)
            print(diameters)
            analysis, created = AnalysisResult.objects.get_or_create(sample=sample)
            analysis.metric_1 = metric_1
            analysis.metric_2 = metric_2
            analysis.diameters = [float(x) for x in diameters]
            print(analysis.diameters)

            if hist1_path:
                with open(hist1_path, "rb") as f:
                    analysis.histogram_1.save(f"hist1_{sample.id}.png", ContentFile(f.read()), save=False)

            if overlay_path:
                with open(overlay_path, "rb") as f:
                    analysis.overlay.save(f"overlay_{sample.id}.png", ContentFile(f.read()), save=False)

            analysis.save()

            # метрики собираем из базы (вдруг часть уже была)
            metrics_1.append(analysis.metric_1)
            metrics_2.append(analysis.metric_2)
            print(sample.analysis.diameters)
            global_diam.extend(analysis.diameters)
        else:
            metrics_1.append(sample.analysis.metric_1)
            metrics_2.append(sample.analysis.metric_2)
            print(sample.analysis.diameters)
            global_diam.extend(sample.analysis.diameters)

    # --- создаем гистограмму для metrics_2 ---
    if metrics_2:
        fig, ax = plt.subplots()
        print(metrics_2)
        ax.hist(metrics_2, bins=20, color="green", alpha=0.7)
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        project.global_metrics2_hist.save("global_metrics2.png", ContentFile(buf.read()), save=False)
        buf.close()
        plt.close(fig)

    # --- создаем гистограмму для global_diam ---
    if global_diam:
        fig, ax = plt.subplots()
        ax.hist(global_diam, bins=20, color="blue", alpha=0.7)
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        project.global_diam_hist.save("global_diam.png", ContentFile(buf.read()), save=False)
        buf.close()
        plt.close(fig)

    # --- обновляем общую инфу в проекте ---
    project.global_stats = {
        "mean_metric1": sum(metrics_1) / len(metrics_1) if metrics_1 else None,
        "metric2": metrics_2 if metrics_2 else None,
        "mean_metric2": sum(metrics_2) / len(metrics_2) if metrics_2 else None,
        "metric2": metrics_2 if metrics_2 else None,
        "global_diam": global_diam if global_diam else None,
        "global_metrics2_hist": project.global_metrics2_hist.name if metrics_2 else None,
        "global_diam_hist": project.global_diam_hist.name if global_diam else None,
    }

    project.save()

    return redirect("project_detail", project_id=project.id)

@login_required
def sample_detail(request, sample_id):
    sample = get_object_or_404(Sample, id=sample_id, project__user=request.user)
    analysis = getattr(sample, "analysis", None)

    hist = overlay = None
    if analysis:
        if analysis.histogram_1:
            hist = analysis.histogram_1.url
        if analysis.overlay:
            overlay = analysis.overlay.url

    return render(request, "sample_detail.html", {
        "sample": sample,
        "analysis": analysis,
        "hist": hist,
        "overlay": overlay,
    })

'''
@login_required
def sample_detail(request, sample_id):
    sample = get_object_or_404(Sample, id=sample_id, project__user=request.user)
    analysis = getattr(sample, "analysis", None)

    chart1 = chart2 = None
    if analysis and analysis.histogram_1 and analysis.overlay:
        chart1 = analysis.histogram_1.url
        chart2 = analysis.overlay.url

    return render(request, "sample_detail.html", {
        "sample": sample,
        "analysis": analysis,
        "chart1": chart1,
        "chart2": chart2,
    })
'''
'''@login_required
def sample_detail(request, sample_id):
    sample = get_object_or_404(Sample, id=sample_id)

    def make_hist(data):
        fig, ax = plt.subplots()
        ax.hist(data, bins=20, color="blue", alpha=0.7)
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        plt.close(fig)
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    chart1 = make_hist(sample.hist_data_1)  # поле модели или JSONField
    chart2 = make_hist(sample.hist_data_2)

    return render(request, "sample_detail.html", {
        "sample": sample,
        "chart1": chart1,
        "chart2": chart2,
        "number1": sample.metric_1,
        "number2": sample.metric_2,
    })'''

    
    
    
'''# --- Сохраняем гистограмму 1 ---
            fig, ax = plt.subplots()
            ax.hist(hist1_values, bins=20, color="blue", alpha=0.7)
            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            analysis.histogram_1.save(f"hist1_{sample.id}.png", ContentFile(buf.read()), save=False)
            buf.close()
            plt.close(fig)

            # --- Сохраняем гистограмму 2 ---
            fig, ax = plt.subplots()
            ax.hist(hist2_values, bins=20, color="green", alpha=0.7)
            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            analysis.histogram_2.save(f"hist2_{sample.id}.png", ContentFile(buf.read()), save=False)
            buf.close()
            plt.close(fig)'''