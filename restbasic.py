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