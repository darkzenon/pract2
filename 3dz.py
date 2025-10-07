from pyproj import Geod
from shapely.geometry import LineString, Point, Polygon
from pyproj import Transformer
from IPython.display import HTML, display
import random
import math

# === 1. Задаем стартовую точку: ваше текущее местоположение ===
startPoint = Point(50.168647, 53.202177)  # Самара
# === 2. Генерация псевдослучайного полигона вокруг стартовой точки ===
lst = []
j = 1
count_p = 10 + round(7 * random.random())  # от 10 до 17 вершин
center_x = startPoint.x
center_y = startPoint.y
while j < count_p:
    radius = 0.0021 * (0.1 + random.random())  # ~200–400 метров
    angle = j * 2 * math.pi / count_p
    lat = center_x + radius * math.cos(angle)
    lon = center_y + radius * math.sin(angle)
    lst.append([lat, lon])
    j += 1
polygon = Polygon(lst)

# === 3. Подсчёт площади и периметра на эллипсоиде WGS84 ===
geod = Geod(ellps="WGS84")
poly_area, poly_perimeter = geod.geometry_area_perimeter(polygon)
area_m2 = abs(poly_area)  # площадь всегда положительна
perimeter_m = abs(poly_perimeter)

# === 4. Пересчёт из EPSG:4326 в EPSG:3857 ===
transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
transformed_coords = list(transformer.itransform(polygon.exterior.coords))

# === 5. Формирование HTML-отчёта ===
# SVG-картинка полигона в исходных координатах (EPSG:4326)
svg_polygon = polygon._repr_svg_()

# Форматируем пересчитанные координаты
coords_str = ""
for x, y in transformed_coords:
    coords_str += f"[{x:.2f}, {y:.2f}]<br>"

result_html = f'''<html>
    <body>
      <h1>Отчёт за Неделю 3. Перепроецирование с использованием pyproj</h1>
      <h2>Выполнил: Горынин Денис Дмитриевич, группа: 2024-ФГиИБ-ИСиТ-2см</h2>

      <h3>Исходный полигон (EPSG:4326)</h3>
      {svg_polygon}

      <h3>Площадь и периметр</h3>
      <p>Площадь: {area_m2:.2f} кв. метров</p>
      <p>Периметр: {perimeter_m:.2f} метров</p>

      <h3>Пересчитанные координаты (EPSG:3857 — Pseudo-Mercator, метры)</h3>
      <p>Система координат: EPSG:3857 (Web Mercator)</p>
      <p>Координаты вершин (X, Y в метрах):</p>
      <div>{coords_str}</div>
    </body>
</html>'''

# Сохранение в файл
file_html = open("result_3.html", "w", encoding="utf-8")
file_html.write(result_html)
file_html.close()

# Отображение для отладки
display(HTML(polygon._repr_svg_()))