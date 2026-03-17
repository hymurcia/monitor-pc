# Monitor de PC

[![Monitor de PC](https://img.shields.io/badge/Monitor%20de%20PC-Flask%20%2B%20psutil-blue)](https://github.com/hymurcia/monitor-pc)

Una aplicación web desarrollada con **Flask** y **psutil** para monitorear en tiempo real el uso de recursos del sistema (CPU, RAM y Disco) directamente desde el navegador.

## ✨ Características

- **Interfaz Web en Tiempo Real:** Dashboard visual con actualización cada 2 segundos.
- **Gráficos Históricos:** Gráficos de líneas interactivos que muestran la tendencia del uso de recursos (usando Chart.js).
- **Monitoreo Detallado:**
  - **CPU:** Porcentaje de uso total.
  - **RAM:** Porcentaje de memoria virtual utilizada.
  - **Disco:**
    - **Actividad (Rendimiento):** Velocidad de lectura/escritura actual (mostrada en la barra de progreso).
    - **Espacio Utilizado:** Capacidad de almacenamiento ocupada (mostrada en texto).
- **Alertas Visuales:** Notificaciones emergentes cuando los recursos superan el 90%.
- **Colores Dinámicos:** Las barras de progreso cambian de color (verde → amarillo → naranja → rojo) según el nivel de carga.
- **Logging:** Registra eventos de alta utilización en `system_monitor.log`.

## 📋 Requisitos Previos

- Python 3.7 o superior.
- Acceso a internet (para cargar la librería Chart.js desde CDN).

## 🚀 Instalación y Configuración

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/hymurcia/monitor-pc.git
    cd monitor-pc
    ```

2.  **Crear un entorno virtual (Opcional pero recomendado):**
    ```bash
    python -m venv venv
    # Activar en Windows:
    venv\Scripts\activate
    # Activar en Linux/Mac:
    source venv/bin/activate
    ```

3.  **Instalar las dependencias:**
    El archivo `requirements.txt` ya contiene las librerías necesarias.
    ```bash
    pip install -r requirements.txt
    ```

## ▶️ Ejecución

1.  Asegúrate de que el entorno virtual esté activado (si lo creaste).
2.  Ejecuta la aplicación:
    ```bash
    python app.py
    ```
3.  Abre tu navegador y ve a:
    ```
    http://127.0.0.1:5000
    ```

## 📁 Estructura del Proyecto

```
monitor_pc/
├── app.py                  # Código principal del servidor Flask
├── requirements.txt        # Dependencias del proyecto
├── system_monitor.log      # Archivo de registro de eventos
├── templates/
│   └── index.html          # Plantilla HTML con CSS y JavaScript
└── README.md               # Este archivo
```

## 🛠️ Tecnologías Utilizadas

- **Backend:** Python, Flask, psutil.
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla).
- **Gráficos:** Chart.js (cargado vía CDN).

## 📊 Cómo Funciona

1.  **Servidor (Flask):**
    *   La ruta `/` renderiza la página principal con los valores iniciales.
    *   La ruta `/data` devuelve un JSON con las métricas actualizadas:
        *   `cpu`: Porcentaje de CPU.
        *   `ram`: Porcentaje de RAM.
        *   `disk_space`: Porcentaje de espacio ocupado en disco.
        *   `disk_activity`: Porcentaje de actividad (rendimiento) del disco.
2.  **Cliente (Navegador):**
    *   JavaScript solicita datos a `/data` cada 2 segundos.
    *   Actualiza las barras de progreso, el texto y el gráfico de Chart.js.
    *   Muestra alertas visuales si algún recurso supera el 90%.

## ⚠️ Notas

*   **Windows:** La ruta del disco por defecto es `C:/`.
*   **Linux/Mac:** La ruta del disco por defecto es `/`.
*   El "Espacio Utilizado" del disco es estático (solo cambia si instalas programas o guardas archivos grandes). La "Actividad del Disco" es dinámica y refleja la velocidad de lectura/escritura actual.

## 📝 Licencia

Este proyecto es de código abierto.