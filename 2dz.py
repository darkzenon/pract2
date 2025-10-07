import random
import math
import folium
import numpy as np
from shapely import wkt, Point, Polygon, LineString, GeometryCollection


# ===========================
# 1. Генерация случайных геометрий
# ===========================

def createRandomWkt(startX, startY, delta=0.07, hasPoints=True, hasLines=True, hasPoly=True, LatLon=False):
    startWkt= "GEOMETRYCOLLECTION("
    points=""
    if hasPoints:
        points_count = 1 + round(10*random.random())
        i = 0
        while i < points_count:
            ra = math.pi*random.random()
            ok = delta*random.random()
            lat = str(startX+ok*math.cos(ra))
            lon = str(startY+ok*math.sin(ra))
            if LatLon:
                points = points + "POINT ("+lon+" "+lat+")"
            else:
                points = points + "POINT ("+lat+" "+lon+")"
            if (i<points_count - 1):
                points=points +", "
            i = i+1
    lines=""
    if hasLines:
        lines_count = 1 + round(5*random.random())
        i = 0
        if hasPoints:
            lines = ", "
        while i < lines_count:
            cur_line = "LINESTRING ("
            j = 0
            i = i+1
            count_p = 2 + round(3*random.random())
            while j < count_p:
                ra = math.pi*random.random()
                ok = delta*random.random()
                lat = str(startX+ok*math.cos(ra))
                lon = str(startY+ok*math.sin(ra))
                if LatLon:
                    cur_line = cur_line + lat +" "+ lon
                else:
                    cur_line = cur_line + lon +" "+ lat
                if (j<count_p - 1):
                    cur_line=cur_line +", "
                j = j+1
            cur_line = cur_line+")"
            lines = lines + cur_line
            if i < lines_count:
                lines=lines +", "
    polys=""
    if hasPoly:
        poly_count =  1 + round(5*random.random())
        if hasPoints or hasLines:
            polys = ", "
        i = 0
        while i < poly_count:
            cur_poly = "POLYGON (("
            j = 1
            i = i+1
            count_p = 3 + round(7*random.random())
            center_x = startX+0.5*delta*math.cos(math.pi*random.random())
            center_y = startY+0.5*delta*math.sin(math.pi*random.random())
            str_first=""
            while j < count_p:
                radius = delta*0.3*(0.1+random.random())
                angle = j*2*math.pi/count_p
                lat = str(center_x+radius*math.cos(angle))
                lon = str(center_y+radius*math.sin(angle))
                if LatLon:
                    if j == 1:
                        str_first = lat+" "+lon
                    cur_poly = cur_poly +lat +" "+ lon
                else:
                    if j == 1:
                        str_first = lon+" "+lat
                    cur_poly = cur_poly +lon +" "+ lat
                cur_poly=cur_poly +", "
                j = j+1
            cur_poly = cur_poly+str_first+"))"
            polys = polys + cur_poly
            if i < poly_count:
                polys=polys +", "
    finishWkt = ")"
    return startWkt + points + lines + polys + finishWkt

# === Укажите свои координаты ===
wkt_str = createRandomWkt(50.168647, 53.202177, delta=0.03, LatLon=False)

# Сохраняем и загружаем
with open('geom.wkt', 'w') as f:
    f.write(wkt_str)
geom_objects = wkt.loads(wkt_str)

# ===========================
# 2. Пространственный анализ
# ===========================

def get_type_name(g):
    if isinstance(g, Point): return "Точка"
    if isinstance(g, LineString): return "Ломаная"
    if isinstance(g, Polygon): return "Полигон"
    return "Объект"

analysis_lines = []
geoms = list(geom_objects.geoms)

for i, g1 in enumerate(geoms):
    for j in range(i + 1, len(geoms)):
        g2 = geoms[j]
        t1, t2 = get_type_name(g1), get_type_name(g2)

        if not isinstance(g1, Point) and not isinstance(g2, Point):
            if g1.intersects(g2):
                analysis_lines.append(f"{t1} {i} пересекается с {t2.lower()} {j}")

        # Точка в полигоне
        if isinstance(g1, Point) and isinstance(g2, Polygon):
            if g2.contains(g1):
                analysis_lines.append(f"{t1} {i} входит в {t2.lower()} {j}")
        elif isinstance(g2, Point) and isinstance(g1, Polygon):
            if g1.contains(g2):
                analysis_lines.append(f"{t2} {j} входит в {t1.lower()} {i}")

# ===========================
# 3. Визуализация на карте
# ===========================

# Определяем центр и масштаб
all_lats, all_lons = [], []
for g in geoms:
    if isinstance(g, Polygon):
        coords = g.exterior.coords
        for coord in coords:
            lon, lat = coord[0], coord[1]
            all_lats.append(lat)
            all_lons.append(lon)

center_lat = (min(all_lats) + max(all_lats)) / 2
center_lon = (min(all_lons) + max(all_lons)) / 2


print(center_lat)
print(center_lon)


m = folium.Map(
    location=[center_lon, center_lat],
    zoom_start=13,
    control_scale=True,
    tiles='OpenStreetMap'
)

for i, g in enumerate(geoms):
    tooltip = str(i)
    popup = f"{get_type_name(g)} {i}"

    if isinstance(g, Polygon):
        folium.Polygon(
            locations=np.array(g.exterior.coords),
            color="blue",
            weight=2,
            fill_color="lightblue",
            fill_opacity=0.5,
            popup=popup,
            tooltip=tooltip
        ).add_to(m)
    elif isinstance(g, LineString):
        folium.PolyLine(
            locations=np.array(g.coords),
            color="gray",
            weight=2,
            popup=popup,
            tooltip=tooltip
        ).add_to(m)
    elif isinstance(g, Point):
        folium.Marker(
            location=[g.y, g.x],  # [lat, lon]
            popup=popup,
            tooltip=tooltip
        ).add_to(m)

# Получаем HTML карты как строку
map_html = m._repr_html_()

# ===========================
# 4. Формирование итогового отчёта
# ===========================

html_content = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Отчёт за 2 неделю</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2 {{ color: #2c3e50; }}
        ul {{ line-height: 1.6; }}
        pre {{ background: #f8f9fa; padding: 10px; border-radius: 4px; overflow-x: auto; }}
    </style>
</head>
<body>
    <h1>Отчет за 2 неделю ознакомительной практики по разработке программного обеспечения геосервиса</h1>
    <h2>Выполнил: Горынин Денис Дмитриевич, группа: 2024-ФГиИБ-ИСиТ-2см</h2>

    <h3>Исходные данные (WKT):</h3>
    <pre>{geom_objects.wkt}</pre>

    <h3>Результаты пространственного анализа:</h3>
    <ul>
'''

for line in analysis_lines:
    html_content += f"        <li>{line}</li>\n"
    print(line)

html_content += '''    </ul>

    <h3>Карта:</h3>
'''

# Вставляем карту
html_content += map_html

html_content += '''
</body>
</html>
'''

# Сохраняем
with open("result_2.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Отчёт сохранён в файл: result_2.html")