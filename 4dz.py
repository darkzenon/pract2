import pandas as pd
import shapely
import ast
import folium
from folium.plugins import MarkerCluster
from IPython.display import HTML, display

# === ФУНКЦИЯ ПАРСИНГА ПОЛИГОНА ===
# === ФУНКЦИЯ ПАРСИНГА ПОЛИГОНА ===
def parse_coordinates(coord_str):
    try:
        coords_list = ast.literal_eval(coord_str)[0]
        return [(lon, lat) for lat, lon in coords_list]
    except:
        return None


# === ЗАГРУЗКА ДАННЫХ ===
df_regions = pd.read_csv('russian_regions.csv', sep=';', encoding='cp1251')
df_objects = pd.read_csv('objects_v2.csv', sep=';', encoding='utf-8', low_memory=False)

# === ДАННЫЕ ===
MY_REGION = "Самарская область"
MY_STREETS = ["Ленина", "Гагарина", "Победы"]  # улицы

# === НАХОЖДЕНИЕ ПОЛИГОНА РЕГИОНА ===
region_row = df_regions[df_regions['Регион'] == MY_REGION]
coords = parse_coordinates(region_row.iloc[0]['Полигон'])

polygon = shapely.Polygon(coords)
centroid = polygon.centroid
map_center = [centroid.y, centroid.x]

# === СОЗДАНИЕ КАРТЫ ===
m = folium.Map(location=map_center, zoom_start=9, tiles='OpenStreetMap')
folium_coords = [(lat, lon) for lon, lat in coords]

# Полигон региона
folium.Polygon(
    locations=folium_coords,
    tooltip=MY_REGION,
    color='darkgreen',
    weight=2,
    fill=True,
    fillColor='lightgreen',
    fillOpacity=0.25
).add_to(m)

# === ПОДГОТОВКА ДАННЫХ ОБЪЕКТОВ ===
df_objects = df_objects.dropna(subset=['latitude', 'longitude'])
df_objects['latitude'] = pd.to_numeric(df_objects['latitude'], errors='coerce')
df_objects['longitude'] = pd.to_numeric(df_objects['longitude'], errors='coerce')
df_objects = df_objects.dropna(subset=['latitude', 'longitude'])

# === ДОБАВЛЕНИЕ МАРКЕРОВ ЧЕРЕЗ CLUSTER ===
marker_cluster = MarkerCluster().add_to(m)

added_count = 0
for idx, row in df_objects.iterrows():
    try:
        point = shapely.Point(row['longitude'], row['latitude'])
        address = str(row['address']) if pd.notna(row['address']) else ""
        
        if shapely.contains(polygon, point):
            if any(street in address for street in MY_STREETS):
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=row['address'],
                    tooltip=row['name']
                ).add_to(marker_cluster)
                added_count += 1
    except:
        continue

# === ГЕНЕРАЦИЯ HTML-ОТЧЁТА ===

# Информационный блок
info_block = f'''
<div style="font-family: Arial, sans-serif; margin: 20px; background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #27ae60;">
    <h1 style="color: #2c3e50;">Неделя 4. Пространственные запросы и пространственные операции</h1>
    <h2 style="color: #3498db;">Выполнил: Горынин Денис Дмитриевич, группа: 2024-ФГиИБ-ИСиТ-2см</h2>
    <p><strong>Регион:</strong> {MY_REGION}</p>
    <p><strong>Выбранные улицы:</strong> {', '.join(MY_STREETS)}</p>
    <p><strong>Найдено объектов:</strong> {added_count}</p>
    <p><strong>Центр карты:</strong> {map_center[0]:.6f}, {map_center[1]:.6f} (широта, долгота)</p>
</div>
'''

# Получаем полный HTML от карты
map_html = m.get_root().render()

# Вставляем заголовок в начало body
full_html = map_html.replace('<body>', '<body>\n' + info_block, 1)

# Сохраняем
with open("result_4.html", "w", encoding="utf-8") as f:
    f.write(full_html)

print(f"Отчёт сохранён в result_4.html")
print(f"Регион: {MY_REGION}")
print(f"Улицы: {MY_STREETS}")
print(f"Найдено объектов: {added_count}")