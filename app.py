import streamlit as st
import pandas as pd

# ----------------------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Buscador GRD",
    page_icon="🔎",
    layout="centered" 
)

st.title("🔎 Consulta de Puntos de Corte GRD")
st.write("Esta herramienta consulta el Punto de Corte Superior (PC sup) de la norma GRD.")

# ----------------------------------------------------------------------
# CARGA DE DATOS (No hay cambios aquí)
# ----------------------------------------------------------------------
@st.cache_data
def cargar_datos():
    try:
        df = pd.read_excel(
            "BD_Norma.xlsx", 
            sheet_name="BD_Norma", 
            header=0
        )
        if len(df.columns) < 15:
            st.error(f"Error: La hoja 'BD_Norma' no se cargó correctamente.")
            return None, None, None
        
        col_grd_nombre = df.columns[0]
        col_pc_nombre = df.columns[14]
        df[col_grd_nombre] = df[col_grd_nombre].astype(str).str.zfill(6)
        
        return df, col_grd_nombre, col_pc_nombre
    
    except FileNotFoundError:
        st.error(f"Error CRÍTICO: No se encontró el archivo 'BD_Norma.xlsx'.")
        return None, None, None
    except Exception as e:
        st.error(f"Error inesperado al cargar los datos: {e}")
        return None, None, None

# --- Fin de la función 'cargar_datos' ---

# 1. Ejecutamos la función
df, col_grd, col_pc = cargar_datos()

# ----------------------------------------------------------------------
# INTERFAZ DE BÚSQUEDA (CON st.form Y 2 BOTONES)
# ----------------------------------------------------------------------
if df is not None:

    # --- Gestión de Estado (El cerebro de la app) ---
    
    # Inicializamos las variables en el estado si no existen
    if "grd_input" not in st.session_state:
        st.session_state.grd_input = ""
    if "search_result" not in st.session_state:
        st.session_state.search_result = None # Aquí guardaremos el resultado

    # Callback para el botón "Limpiar"
    def clear_all_state():
        st.session_state.grd_input = ""
        st.session_state.search_result = None # ¡Borra también el resultado!

    # --- El Formulario de Búsqueda ---
    # Usamos un 'form' para que la app no se recargue
    # hasta que presionemos "Buscar".
    with st.form(key="search_form"):
        
        # 1. El Input (controlado por session_state)
        codigo_ingresado = st.text_input(
            label="Ingrese Código GRD:", 
            max_chars=6,
            placeholder="Ingrese el código de 6 dígitos (ej: 011202)",
            key="grd_input" # Vinculado al estado
        )
        
        # 2. El Botón "Buscar" (dentro del form)
        submit_button = st.form_submit_button(label="Buscar")

    # 3. El Botón "Limpiar" (FUERA del form)
    st.button("Limpiar", on_click=clear_all_state)

    # --- Lógica de Búsqueda (SOLO si se presionó "Buscar") ---
    if submit_button:
        if codigo_ingresado:
            codigo_buscado = codigo_ingresado.zfill(6)
            resultado = df[df[col_grd] == codigo_buscado]
            
            if not resultado.empty:
                valor_pc = resultado.iloc[0][col_pc]
                # Guardamos el resultado en el estado
                st.session_state.search_result = ("success", f"**Punto de Corte (Sup): {valor_pc}**")
            else:
                if len(codigo_ingresado) == 6:
                    st.session_state.search_result = ("error", "Código GRD no encontrado.")
                else:
                    # Este caso es raro con el form, pero por seguridad
                    st.session_state.search_result = ("info", "Buscando...")
        else:
            st.session_state.search_result = ("info", "Por favor, ingrese un código.")

    # --- Lógica de Visualización (Se ejecuta siempre) ---
    # Esta sección solo "lee" lo que hay en el estado y lo dibuja.
    if st.session_state.search_result:
        msg_type, message = st.session_state.search_result
        if msg_type == "success":
            st.success(message)
        elif msg_type == "error":
            st.error(message)
        elif msg_type == "info":
            st.info(message)