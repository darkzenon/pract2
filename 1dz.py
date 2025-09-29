import pandas as pd
from geopy.distance import geodesic
import random
import folium

# === 1. Чтение данных ===
df = pd.read_csv('Rus_schools_final.csv', encoding='windows-1251')

# === 2. Генерация случайной точки в пределах России (bbox) ===
# Bounding box для России (центральная часть )
bbox = {
    'min_lat': 52.0,
    'max_lat': 60.0,
    'min_lon': 29.0,   
    'max_lon': 63.0   
}

# Генерация случайных координат внутри bbox России
lat_home = round(random.uniform(bbox['min_lat'], bbox['max_lat']), 3)
lon_home = round(random.uniform(bbox['min_lon'], bbox['max_lon']), 3)
point_home = (lat_home, lon_home)

print(f"Сгенерированы случайные координаты дома: {point_home}")

# === 3. Нахождение ближайшей школы к дому ===
def calculate_distance(row):
    return geodesic((row['lat'], row['lon']), point_home).kilometers

df['distance'] = df.apply(calculate_distance, axis=1)
closest_school = df.loc[df['distance'].idxmin()]

# === 4. Все школы в радиусе 3 км от дома ===
schools_within_3km = df[df['distance'] <= 30]

# === 5. школЫ с типом "Государственное образовательное учреждение" ===
gov_schools = df[df['struct'] == '(Государственное образовательное учреждение)']
count_gov_schools = len(gov_schools)

# === 6. HTML с картой ===
html_content = f'''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Отчет по практике</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            background-color: #f7f9fc;
            color: #333;
            margin: 0;
            padding: 20px;
            line-height: 1.7;
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #2980b9;
        }}
        .section {{
            background-color: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        table, th, td {{
            border: 1px solid #ddd;
        }}
        th, td {{
            padding: 10px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        .highlight {{
            background-color: #ecf0f1;
            padding: 10px;
            border-left: 4px solid #3498db;
            font-weight: bold;
        }}
        #map {{
            height: 500px;
            border-radius: 8px;
            margin-top: 20px;
            position: relative !important;
        }}
    </style>
</head>
<body>

    <h1>Отчет за 1 неделю ознакомительной практики по разработке программного обеспечения геосервиса</h1>
    <h2>Выполнил: Горынин Денис Дмитриевич, группа: 2024-ФГиИБ-ИСиТ-2см</h2>

    <div class="section">
        <h2>1. Ближайшая школа рандомному дому</h2>
        <p><strong>Координаты дома:</strong> {lat_home:.6f}, {lon_home:.6f}</p>
        <div class="highlight">
            <strong>Название:</strong> {closest_school['name']}<br>
            <strong>Адрес:</strong> {closest_school['addr']}<br>
            <strong>Тип учреждения:</strong> {closest_school['struct']}<br>
            <strong>Широта:</strong> {closest_school['lat']}<br>
            <strong>Долгота:</strong> {closest_school['lon']}<br>
            <strong>Расстояние до дома:</strong> {closest_school['distance']:.3f} км
        </div>
    </div>

    <div class="section">
        <h2>2. Все школы в радиусе 30 км от дома</h2>
        {('<p>Найдено ' + str(len(schools_within_3km)) + ' школ(ы):</p>') if len(schools_within_3km) > 0 else '<p>В радиусе 30 км школ не найдено.</p>'}
        
        <table>
            <tr>
                <th>Название школы</th>
                <th>Адрес</th>
                <th>Расстояние (км)</th>
            </tr>
'''

# Добавляем строки таблицы
for _, row in schools_within_3km.iterrows():
    html_content += f'''
            <tr>
                <td>{row["name"]}</td>
                <td>{row["addr"]}</td>
                <td>{row["distance"]:.3f}</td>
            </tr>
    '''

html_content += '''
        </table>
    </div>

    <div class="section">
        <h2>3. Количество школ типа "Государственное образовательное учреждение"</h2>
        <p class="highlight">Всего: {'''+str(count_gov_schools)+'''} школ(а)</p>
    </div>

    <div class="section">
        <h2>4. Интерактивная карта</h2>
        <p>На карте показаны:</p>
        <ul>
            <li>Ваш дом (красный маркер)</li>
            <li>Ближайшая школа (зелёный маркер)</li>
            <li>Все школы в радиусе 3 км (синие маркеры)</li>
        </ul>
        <div id="map"></div>
    </div>

</body>
</html>
'''

# === 7. Создание карты с помощью Folium ===
m = folium.Map(location=point_home, zoom_start=12, tiles="OpenStreetMap")

# Маркер дома
folium.Marker(
    location=point_home,
    popup=f"Ваш дом<br>{lat_home:.6f}, {lon_home:.6f}",
    icon=folium.Icon(color="red", icon="home")
).add_to(m)

# Маркер ближайшей школы
folium.Marker(
    location=[closest_school['lat'], closest_school['lon']],
    popup=f"Ближайшая школа:<br>{closest_school['name'][:50]}...",
    tooltip=closest_school['name'],
    icon=folium.Icon(color="green", icon="school")
).add_to(m)

# Маркеры всех школ в радиусе 30 км
for _, school in schools_within_3km.iterrows():
    folium.CircleMarker(
        location=[school['lat'], school['lon']],
        radius=6,
        popup=school['name'],
        tooltip=school['name'],
        color="blue",
        fill=True,
        fillColor="blue"
    ).add_to(m)

# Сохраняем карту как HTML-фрагмент
map_html = m.get_root().render()

# Находим место для вставки карты
insert_marker = '<div id="map"></div>'
html_content = html_content.replace(insert_marker, f'<div id="map">{map_html}</div>')

# === 8. Сохранение финального HTML ===
with open("result.html", "w", encoding="utf-8") as file:
    file.write(html_content)

print("Файл 'result.html' успешно создан!")