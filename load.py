import pandas as pd
import folium
import webbrowser

path = 'C:/Users/svanruijven/PycharmProjects/ODW/data/clean/MTM logfiles 12-08-2022/clean_lamp_12-08-2022.csv'
df = pd.read_csv(path)

# Coordinates for Base map NL
NL = [52.2434979, 5.6343227]
m = folium.Map(NL, zoom_start = 8)

def color(value):
    if value == 'cat 2':
        return 'orange'
    if value == 'cat 4':
        return 'red'
    else:
        return 'green'

color = map(color, df['categorie'])
colorlist = list(color)
len(colorlist)
df['kleur'] = colorlist

for i in range(0, len(df)):
    try:
        folium.Marker([df.iloc[i]['Y'], df.iloc[i]['X']],
                        popup = folium.Popup(f"<b>Maximo location:</b><br>{df.iloc[i]['asset']}</br>", max_width=300, min_width=150),
                        tooltip = f"<b>Fout: {df.iloc[i]['fout']}</b><br>Beeld: {df.iloc[i]['beeld']}<br>MSI-type: {df.iloc[i]['msi_type']}<br>Locatie: {df.iloc[i]['wegsoort']} {df.iloc[i]['Wegnummer']} {df.iloc[i]['hm']} {df.iloc[i]['baansoort']} {df.iloc[i]['rijrichting']} {int(df.iloc[i]['strooknummer_new'])}<br>Duur storing: {df.iloc[i]['duur']} dagen<br>Categorie storing: {df.iloc[i]['categorie']}",
                        icon = folium.Icon(color=df.iloc[i]['kleur'], icon="info-sign")).add_to(m)
    except:
        pass

m.save('map.html')

webbrowser.open('map.html')  # open file in webbrowser

def main():
    print('[Load] Load data and create map view')