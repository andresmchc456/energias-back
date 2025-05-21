import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


df = pd.read_csv(r"c:\Users\ELIAS\Desktop\trabajos_graficas\graficas2\energia.csv")  


countries = ["Africa", "Asia", "Europe"]  


df_selected = df[df["Entity"].isin(countries)].copy()
df_selected = df_selected.sort_values(["Entity", "Year"])


data_by_country = {
    country: {
        "years": group["Year"].values,
        "renewables": group["Renewables (% equivalent primary energy)"].values
    }
    for country, group in df_selected.groupby("Entity")
}


fig, ax = plt.subplots()
ax.set_xlim(df_selected["Year"].min(), df_selected["Year"].max())
ax.set_ylim(0, df_selected["Renewables (% equivalent primary energy)"].max() + 5)
ax.set_title("Energía Renovable por Región")
ax.set_xlabel("Año")
ax.set_ylabel("Renovables (% energía primaria)")
ax.grid(True)


lines = {}
for i, country in enumerate(data_by_country.keys()):
    lines[country], = ax.plot([], [], lw=2, label=country)  


ax.legend(loc="upper left")


def init():
    for line in lines.values():
        line.set_data([], [])
    return lines.values()

def update(frame):
    for country, line in lines.items():
        x = data_by_country[country]["years"][:frame+1]
        y = data_by_country[country]["renewables"][:frame+1]
        line.set_data(x, y)
    return lines.values()

ani = FuncAnimation(fig, update, frames=len(df_selected["Year"].unique()), init_func=init, blit=True, interval=150)


ani.save("renewables_by_region.gif", writer="pillow", fps=5)


 plt.show()