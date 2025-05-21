import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # O ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/paises")
def get_paises():
    df = pd.read_csv(r"C:\Users\User\Desktop\Copia de seguridad\boot cam\proyecto final\SERVIDORES\SERVIDORES\trabajos_graficas\graficas2\energia.csv")
    paises = df["Entity"].unique().tolist()
    return {"paises": paises}

@app.get("/anios")
def get_anios(entity: str):
    df = pd.read_csv(r"C:\Users\User\Desktop\Copia de seguridad\boot cam\proyecto final\SERVIDORES\SERVIDORES\trabajos_graficas\graficas2\energia.csv")
    anios = df[df["Entity"] == entity]["Year"].unique().tolist()
    anios.sort()
    return {"anios": anios}

@app.get("/grafica/{Entity}")
def get_grafica(Entity: str, tipo: str = Query("linea")):
    df = pd.read_csv(r"C:\Users\User\Desktop\Copia de seguridad\boot cam\proyecto final\SERVIDORES\SERVIDORES\trabajos_graficas\graficas2\energia.csv")
    df_selected = df[df["Entity"] == Entity].copy()
    df_selected = df_selected.sort_values("Year")

    years = df_selected["Year"].values
    renewables = df_selected["Renewables (% equivalent primary energy)"].values

    os.makedirs("graficas", exist_ok=True)
    gif_path = f"graficas/{Entity}_{tipo}.gif"

    fig, ax = plt.subplots()

    if tipo == "linea":
        ax.set_xlim(years.min(), years.max())
        ax.set_ylim(0, renewables.max() + 5)
        ax.set_title(f"Energía Renovable en {Entity}")
        ax.set_xlabel("Año")
        ax.set_ylabel("Renovables (% energía primaria)")
        ax.grid(True)
        line, = ax.plot([], [], lw=2, label=Entity)
        ax.legend(loc="upper left")

        def init():
            line.set_data([], [])
            return line,

        def update(frame):
            x = years[:frame+1]
            y = renewables[:frame+1]
            line.set_data(x, y)
            return line,

        ani = FuncAnimation(fig, update, frames=len(years), init_func=init, blit=True, interval=150)
        ani.save(gif_path, writer="pillow", fps=5)

    elif tipo == "barras":
        ax.set_xlim(years.min(), years.max())
        ax.set_ylim(0, renewables.max() + 5)
        ax.set_title(f"Energía Renovable en {Entity} (Barras)")
        ax.set_xlabel("Año")
        ax.set_ylabel("Renovables (% energía primaria)")

        def update(frame):
            ax.clear()
            ax.set_xlim(years.min(), years.max())
            ax.set_ylim(0, renewables.max() + 5)
            ax.set_title(f"Energía Renovable en {Entity} (Barras)")
            ax.set_xlabel("Año")
            ax.set_ylabel("Renovables (% energía primaria)")
            ax.bar(years[:frame+1], renewables[:frame+1], color='skyblue')
            return ax.patches

        ani = FuncAnimation(fig, update, frames=len(years), blit=False, interval=150)
        ani.save(gif_path, writer="pillow", fps=5)

    elif tipo == "torta":
        ax.set_title(f"Distribución de Energía Renovable en {Entity} (Animado)")
        def update(frame):
            ax.clear()
            ax.set_title(f"Distribución de Energía Renovable en {Entity} - Año {years[frame]}")
            ax.pie(
                [renewables[frame], 100-renewables[frame]],
                labels=['Renovable', 'No Renovable'],
                autopct='%1.1f%%',
                colors=['green', 'gray']
            )
            return ax.patches

        ani = FuncAnimation(fig, update, frames=len(years), blit=False, interval=150)
        ani.save(gif_path, writer="pillow", fps=5)

    elif tipo == "area":
        convencionales = 100 - renewables  # Asumiendo que el total es 100%
        ax.set_xlim(years.min(), years.max())
        ax.set_ylim(0, 100)
        ax.set_title(f"Consumo de Energía Renovable vs Convencional en {Entity}")
        ax.set_xlabel("Año")
        ax.set_ylabel("% Energía")
        ax.grid(True)

        def update(frame):
            ax.clear()
            ax.set_xlim(years.min(), years.max())
            ax.set_ylim(0, 100)
            ax.set_title(f"Consumo de Energía Renovable vs Convencional en {Entity}")
            ax.set_xlabel("Año")
            ax.set_ylabel("% Energía")
            ax.grid(True)
            ax.stackplot(
                years[:frame+1],
                renewables[:frame+1],
                convencionales[:frame+1],
                labels=['Renovable', 'Convencional'],
                colors=['green', 'gray'],
                alpha=0.7
            )
            ax.legend(loc="upper left")
            return ax.collections

        ani = FuncAnimation(fig, update, frames=len(years), blit=False, interval=50)
        ani.save(gif_path, writer="pillow", fps=15)    

    else:
        plt.close(fig)
        return {"error": "Tipo de gráfica no soportado"}

    plt.close(fig)
    return FileResponse(gif_path, media_type="image/gif")

@app.get("/estimacion-renovable")
def estimacion_renovable(consumo_kwh: float, entity: str, year: int):
    # Rutas de los archivos
    ruta_hidro = r"C:\Users\User\Desktop\Copia de seguridad\boot cam\proyecto final\SERVIDORES\SERVIDORES\trabajos_graficas\fuentes renovables csv\06 hydro-share-energy.csv"
    ruta_viento = r"C:\Users\User\Desktop\Copia de seguridad\boot cam\proyecto final\SERVIDORES\SERVIDORES\trabajos_graficas\fuentes renovables csv\10 wind-share-energy.csv"
    ruta_solar = r"C:\Users\User\Desktop\Copia de seguridad\boot cam\proyecto final\SERVIDORES\SERVIDORES\trabajos_graficas\fuentes renovables csv\14 solar-share-energy.csv"
    ruta_geo = r"C:\Users\User\Desktop\Copia de seguridad\boot cam\proyecto final\SERVIDORES\SERVIDORES\trabajos_graficas\fuentes renovables csv\17 installed-geothermal-capacity.csv"

    # Leer CSVs
    df_hidro = pd.read_csv(ruta_hidro)
    df_viento = pd.read_csv(ruta_viento)
    df_solar = pd.read_csv(ruta_solar)
    df_geo = pd.read_csv(ruta_geo)

    # Filtrar por país y año
    try:
        hidro = df_hidro[(df_hidro["Entity"] == entity) & (df_hidro["Year"] == year)]["Hydro (% equivalent primary energy)"].values[0]
    except IndexError:
        hidro = 0.0
    try:
        viento = df_viento[(df_viento["Entity"] == entity) & (df_viento["Year"] == year)]["Wind (% equivalent primary energy)"].values[0]
    except IndexError:
        viento = 0.0
    try:
        solar = df_solar[(df_solar["Entity"] == entity) & (df_solar["Year"] == year)]["Solar (% equivalent primary energy)"].values[0]
    except IndexError:
        solar = 0.0
    try:
        # Nota: Aquí usamos capacidad instalada como proporción estimada (aproximación)
        geo = df_geo[(df_geo["Entity"] == entity) & (df_geo["Year"] == year)]["Geothermal Capacity"].values[0]
        geo_pct = min((geo / 1000) * 2, 5)  # Aproximación: hasta un 5% si tiene mucha capacidad instalada
    except IndexError:
        geo_pct = 0.0

    # Total porcentaje renovable estimado
    total_pct_renovable = hidro + viento + solar + geo_pct
    total_pct_renovable = min(total_pct_renovable, 100.0)  # No puede superar el 100%

    # Energía renovable estimada en el consumo del usuario
    energia_renovable_kwh = (total_pct_renovable / 100.0) * consumo_kwh

    return {
        "pais": entity,
        "año": year,
        "consumo_total_kwh": consumo_kwh,
        "porcentaje_renovable_estimado": round(total_pct_renovable, 2),
        "consumo_renovable_kwh_estimado": round(energia_renovable_kwh, 2)
    }