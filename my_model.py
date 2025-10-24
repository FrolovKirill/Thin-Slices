import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import torch
import torch.nn as nn
from torchvision.models import resnet50
from torchvision import transforms
# from image_processing import process_image
import cv2 as cv
from skimage import measure, morphology
from skimage.feature import peak_local_max
from skimage.segmentation import watershed
from scipy import ndimage as ndi
import os, sys

def resource_path(relative_path):
    """ Достаёт путь к файлу из exe или из папки проекта """
    if getattr(sys, 'frozen', False):  # если запущено как exe
        base_path = sys._MEIPASS
    else:  # если обычный Python
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def classify_image(image_path):
    """ Пока тут заглушка """
    return np.random.choice([0, 1, 2])

def process_image(image):
    # Конвертируем в numpy array
    im = np.array(image)
    
    # Альтернативный метод 1: работа в HSV пространстве
    hsv = cv.cvtColor(im, cv.COLOR_RGB2HSV)
    
    # Используем saturation и value каналы
    saturation = hsv[:, :, 1].astype(np.float32)
    value = hsv[:, :, 2].astype(np.float32)
    
    # Нормализуем
    saturation_norm = (saturation - saturation.min()) / (saturation.max() - saturation.min() + 1e-8)
    value_norm = (value - value.min()) / (value.max() - value.min() + 1e-8)
    
    # Комбинируем saturation и value
    img1 = saturation_norm * value_norm
    img1 = 255 * (img1 / (img1.max() + 1e-8))
    img1 = img1.astype(np.uint8)
    
    # Адаптивная пороговая обработка вместо Оцу
    th1 = cv.adaptiveThreshold(img1, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, 
                              cv.THRESH_BINARY, 11, 2)
    class1 = (th1 == 255)
    
    # Альтернативный метод 2: лапласиан градиентов + морфологические операции
    img2 = np.array(image.convert('L'))
    
    # Лапласиан для выделения границ
    laplacian = cv.Laplacian(img2, cv.CV_64F)
    laplacian_abs = np.absolute(laplacian)
    laplacian_8u = np.uint8(laplacian_abs / laplacian_abs.max() * 255)
    
    # Морфологическое закрытие для объединения областей
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (5, 5))
    closed = cv.morphologyEx(laplacian_8u, cv.MORPH_CLOSE, kernel)
    
    # Пороговая обработка
    ret2, th2 = cv.threshold(closed, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    class2 = (th2 == 255)
    
    # Разрешение конфликтов: взвешенное объединение
    intersection = class1 & class2
    union = class1 | class2
    
    # Создаем результат с приоритетом уверенных областей
    result = np.zeros_like(img1, dtype=np.uint8)
    
    # Области, обнаруженные обоими методами - высокая уверенность (класс 1)
    result[intersection] = 1
    
    # Области, обнаруженные только HSV методом (класс 2)
    result[class1 & ~intersection] = 2
    
    # Области, обнаруженные только градиентным методом (класс 3)
    result[class2 & ~intersection] = 3
    
    # Все остальное - фон (класс 0)
    result[~union] = 0
    
    return result, class1, class2, intersection

def segment_image(image):
    imggg = np.array(image.convert('L'))
    
    # Бинаризация
    ret, binary = cv.threshold(imggg, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    
    # Connected components
    num_labels, labels, stats, centroids = cv.connectedComponentsWithStats(binary)
    
    diameters = []
    for i in range(1, num_labels):  # пропускаем фон (0)
        area = stats[i, cv.CC_STAT_AREA]
        if area > 50:
            # Диаметр эквивалентной окружности
            diameter = 2 * np.sqrt(area / np.pi)
            diameters.append(diameter)
    
    return diameters
            
def create_overlay(original_path, mask, save_path):
    # читаем исходное изображение
    original = np.array(Image.open(original_path).convert("RGB"))

    # палитра для трёх классов (можно поменять цвета)
    colors = {
        0: (255, 0, 0),     # красный
        1: (0, 255, 0),     # зелёный
        2: (0, 0, 255)      # синий
    }

    # создаём пустое цветное изображение под маску
    mask_rgb = np.zeros_like(original)
    for cls, color in colors.items():
        mask_rgb[mask == cls] = color

    # накладываем с прозрачностью
    alpha = 0.4
    overlay = (original * (1 - alpha) + mask_rgb * alpha).astype(np.uint8)

    # сохраняем
    Image.fromarray(overlay).save(save_path)

    return save_path

def run_full_analysis(image_path):
    image = Image.open(image_path)
    # тут считаешь свои метрики
    masked, _, _, _ = process_image(image)
    diameters = segment_image(image)

    metric_1 = np.mean(diameters)
    metric_2 = np.sum(masked==1) / np.size(masked)

    # сохраняем гистограммы
    hist1_path = "media/analysis/hist1.png"
    plt.figure()
    plt.hist(diameters, bins=10)
    plt.savefig(hist1_path)
    plt.close()
    
    # создаём overlay
    overlay_path = "media/analysis/overlay.png"
    create_overlay(image_path, masked, overlay_path)
    
    
    # hist2_path = "media/analysis/hist2.png"
    '''plt.figure()
    plt.hist(diameters, bins=10)
    plt.savefig(hist2_path)
    plt.close()'''

    # return metric_1, metric_2, hist1_path, hist2_path, overlay_path
    return metric_1, metric_2, hist1_path, overlay_path, diameters