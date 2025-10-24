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
    # Загрузка и обработка изображения первым способом
    im = np.array(image)
    
    # Первый метод: цветовая обработка
    R = (im[:, :, 0] - im[:, :, 0].min()) / (im[:, :, 0].max() - im[:, :, 0].min() + 1e-8)
    G = (im[:, :, 1] - im[:, :, 1].min()) / (im[:, :, 1].max() - im[:, :, 1].min() + 1e-8)
    B = (im[:, :, 2] - im[:, :, 2].min()) / (im[:, :, 2].max() - im[:, :, 2].min() + 1e-8)
    
    img1 = (B - R)
    img1 = img1 - img1.min()
    img1 = 255 * (img1 / (img1.max() + 1e-8))
    img1 = img1.astype(np.uint8)
    
    # Пороговая обработка Оцу
    ret1, th1 = cv.threshold(img1, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    class1 = (th1 == 255)  # Первый класс
    
    # Второй метод: градации серого + Гауссово размытие
    img2 = np.array(image.convert('L'))
    blur = cv.GaussianBlur(img2, (5, 5), 0)
    ret2, th2 = cv.threshold(blur, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    class2 = (th2 == 255)  # Второй класс
    
    # Три метода разрешения конфликтов
    intersection = class1 & class2  # Пересечение классов
    
    # Метод 1: пересечение отдаем в 1 класс
    result_method1 = np.zeros_like(img1, dtype=np.uint8)
    result_method1[class2] = 2  # Сначала назначаем второй класс
    result_method1[class1] = 1  # Перезаписываем первым классом (включая пересечение)
    result_method1[~(class1 | class2)] = 3  # Третий класс
    
    return result_method1, class1, class2, intersection

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