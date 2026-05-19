import streamlit as st
import numpy as np
import os

# Configuración de página
st.set_page_config(page_title="CMR Reference Pro", layout="wide", initial_sidebar_state="expanded")

# --- SIDEBAR (TEMA Y DATOS PACIENTE) ---
with st.sidebar:
    dark_mode = st.toggle("🌙 Modo Oscuro / ☀️ Claro", value=False)
    st.divider()

    st.header("Perfil del Paciente")
    sexo = st.radio("Género", ["Hombre", "Mujer"], horizontal=True)
    sk = "H" if sexo == "Hombre" else "M"
    edad = st.number_input("Edad (años)", 18, 100, 45)
    peso = st.number_input("Peso (kg)", 30.0, 150.0, 75.0)
    altura = st.number_input("Altura (cm)", 100, 220, 175)
    
    def calcular_bsa_dubois(p, a):
        return 0.007184 * (p**0.425) * (a**0.725)
    
    bsa = calcular_bsa_dubois(peso, altura)
    st.divider()
    st.metric("Superficie Corporal (DuBois)", f"{bsa:.2f} m²")

# --- INYECCIÓN DE ESTILOS ---
if dark_mode:
    bg_app = "#121212"
    bg_sidebar = "#1e1e1e"
    bg_card = "#25282f"
    text_color = "#ffffff"
    border_color = "#3b82f6"
    title_color = "#9ca3af"
    val_color = "#60a5fa"
    shadow = "0 4px 6px rgba(0,0,0,0.4)"
    shadow_hover = "0 6px 12px rgba(0,0,0,0.6)"
else:
    bg_app = "#f9fafb"
    bg_sidebar = "#ffffff"
    bg_card = "#ffffff"
    text_color = "#111827"
    border_color = "#0052cc"
    title_color = "#6b7280"
    val_color = "#0052cc"
    shadow = "0 4px 6px rgba(0,0,0,0.05)"
    shadow_hover = "0 6px 12px rgba(0,0,0,0.1)"

st.markdown(f"""
    <style>
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .stApp {{ background-color: {bg_app} !important; color: {text_color} !important; }}
    [data-testid="stSidebar"] {{ background-color: {bg_sidebar} !important; }}
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stText, [data-testid="stMetricValue"] {{ color: {text_color} !important; }}
    .stSelectbox div[data-baseweb="select"] {{ background-color: {bg_card} !important; color: {text_color} !important; }}
    .metric-card {{ background-color: {bg_card}; border-left: 5px solid {border_color}; padding: 20px 25px; border-radius: 8px; box-shadow: {shadow}; margin-bottom: 20px; transition: transform 0.2s, box-shadow 0.2s; }}
    .metric-card:hover {{ transform: translateY(-2px); box-shadow: {shadow_hover}; }}
    .metric-title {{ color: {title_color}; font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }}
    .metric-value {{ color: {val_color}; font-size: 30px; font-weight: 800; }}
    .stSelectbox label {{ font-size: 18px !important; font-weight: 600 !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE SOPORTE CORREGIDAS ---
def format_range(mean, sd):
    return f"{mean - 2*sd:.1f} - {mean + 2*sd:.1f}"

def get_age_bracket(edad, tipo="general"):
    if tipo == "aorta_65":
        if edad < 45: return "<45"
        if 45 <= edad <= 54: return "45-54"
        if 55 <= edad <= 64: return "55-64"
        if 65 <= edad <= 74: return "65-74"
        if 75 <= edad <= 84: return "75-84"
        return ">=85"
    else:
        if edad < 20: return "<20"
        if 20 <= edad <= 29: return "20-29"
        if 30 <= edad <= 39: return "30-39"
        if 40 <= edad <= 49: return "40-49"
        if 50 <= edad <= 59: return "50-59"
        if 60 <= edad <= 69: return "60-69"
        return ">=70"

def mostrar_grid(metricas):
    cols = st.columns(min(len(metricas), 4))
    for i, (titulo, valor) in enumerate(metricas):
        # Ajuste dinámico de fuente para textos largos como "Datos no disponibles"
        val_style = "font-size: 16px; line-height: 1.2;" if "disponible" in str(valor).lower() else ""
        with cols[i % 4]:
            st.markdown(f'''
                <div class="metric-card">
                    <div class="metric-title">{titulo}</div>
                    <div class="metric-value" style="{val_style}">{valor}</div>
                </div>
            ''', unsafe_allow_html=True)

st.title("🏥 CMR Expert: Base de Datos de Referencia")
st.markdown("Valores normales paramétricos ajustados por variables demográficas.")

# --- DICCIONARIO DE MAPEO ---
mapping = {
    "Ventrículo Izquierdo (VI)": "Volumenes VI.jpg",
    "Diámetros VI": "Diametros VI.jpg",
    "Ventrículo Derecho (VD)": "Volumenes VD.jpg",
    "VD por Edad": "Volumenes VD por edad.jpg",
    "Aurícula Izquierda (AI)": "Volumenes AI.jpg",
    "AI por Edad": "Volumenes AI por edad.jpg",
    "AI (Área y Diámetros)": "Area y diametros AI.jpg",
    "Aurícula Derecha (AD)": "Volumenes AD.jpg",
    "AD por Edad": "Volumenes AD por edad.jpg",
    "AD (Área y Diámetros)": "Area y diametros AD.jpg",
    "Aorta (Diámetros)": "Aorta diametros.jpg",
    "Raíz de Aorta por Edad": "Aorta segun edad.jpg",
    "Senos de Valsalva": "Aorta senos de Valsalva.jpg",
    "Arteria Pulmonar": "Arteria pulmonar diametros.jpg",
    "Atletas VI": "Atletas volumenes VI.jpg",
    "Atletas VD": "Atletas volumenes VD.jpg",
    "Mapas Tisulares (T1/T2/ECV)": "Mapa T1.jpg",
    "Diámetro Anillo Mitral": "Anillo mitral.jpg",
    "Diámetro Anillo Tricuspídeo": "Anillo tricuspideo.jpg",
    "Valvulopatía": "Valvulopatia.jpg" 
}

seleccion = st.selectbox("📂 Seleccione la categoría anatómica a consultar:", list(mapping.keys()))
st.divider()

bracket = get_age_bracket(edad)
datos_mostrar = [] 

if seleccion == "Ventrículo Izquierdo (VI)":
    datos_mostrar.extend([
        ("LVEDV (mL)", "81 - 204" if sk=="H" else "68 - 158"),
        ("LVEDV/BSA (mL/m²)", "49 - 102" if sk=="H" else "46 - 90"),
        ("LVESV (mL)", "24 - 82" if sk=="H" else "20 - 67"),
        ("LVESV/BSA (mL/m²)", "15 - 41" if sk=="H" else "14 - 38"),
        ("LVM (g)", "60 - 150" if sk=="H" else "47 - 101"),
        ("LVM/BSA (g/m²)", "39 - 72" if sk=="H" else "33 - 56"),
        ("LVEF (%)", "51 - 77" if sk=="H" else "54 - 79")
    ])

elif seleccion == "Diámetros VI":
    datos_mostrar.extend([
        ("LV end-diastolic 4ch (mm)", "39 - 59" if sk=="H" else "36 - 56"),
        ("LV end-diastolic 4ch/BSA (mm/m²)", "18 - 34" if sk=="H" else "19 - 35"),
        ("LV end-diastolic SAX (mm)", "44 - 61" if sk=="H" else "40 - 56"),
        ("LV end-diastolic SAX/BSA (mm/m²)", "20 - 32" if sk=="H" else "24 - 40")
    ])

elif seleccion == "Ventrículo Derecho (VD)":
    datos_mostrar.extend([
        ("RVEDV (mL)", "74 - 231" if sk=="H" else "59 - 172"),
        ("RVEDV/BSA (mL/m²)", "47 - 116" if sk=="H" else "44 - 99"),
        ("RVESV (mL)", "26 - 104" if sk=="H" else "17 - 75"),
        ("RVESV/BSA (mL/m²)", "16 - 52" if sk=="H" else "13 - 43"),
        ("RV EF (%)", "44 - 72" if sk=="H" else "47 - 75")
    ])

elif seleccion == "VD por Edad":
    st.caption(f"Filtro etario activo: {edad} años")
    if bracket == "<20":
        datos_mostrar.extend([
            ("RVEDV (mL)", "Datos no disponibles para la edad"), ("RVEDV/BSA (mL/m²)", "Datos no disponibles para la edad"),
            ("RVESV (mL)", "Datos no disponibles para la edad"), ("RVESV/BSA (mL/m²)", "Datos no disponibles para la edad"), ("RV EF (%)", "Datos no disponibles para la edad")
        ])
    else:
        vd_age = {
            "H": {"20-29": ("93-254", "56-129", "20-147", "12-73", "27-78"), "30-39": ("81-230", "50-111", "29-113", "18-55", "41-69"), "40-49": ("70-231", "45-114", "21-111", "14-55", "41-72"), "50-59": ("67-225", "42-112", "19-107", "12-55", "44-71"), "60-69": ("50-214", "38-105", "14-93", "12-46", "48-72"), ">=70": ("101-214", "52-106", "34-94", "18-47", "48-71")},
            "M": {"20-29": ("72-176", "51-102", "17-97", "11-55", "35-76"), "30-39": ("68-166", "47-100", "13-86", "9-53", "35-80"), "40-49": ("63-175", "45-97", "17-78", "12-45", "47-75"), "50-59": ("54-167", "41-91", "14-73", "11-41", "49-75"), "60-69": ("54-164", "41-90", "12-68", "10-38", "51-77"), ">=70": ("77-162", "47-90", "22-65", "14-36", "53-75")}
        }
        vals = vd_age[sk][bracket]
        datos_mostrar.extend([
            ("RVEDV (mL)", vals[0]), ("RVEDV/BSA (mL/m²)", vals[1]),
            ("RVESV (mL)", vals[2]), ("RVESV/BSA (mL/m²)", vals[3]), ("RV EF (%)", vals[4])
        ])

elif seleccion == "Aurícula Izquierda (AI)":
    st.caption("Calculado mediante volumen biplano por área longitud.")
    datos_mostrar.extend([
        ("Max LA Volume (mL)", "26 - 110" if sk=="H" else "26 - 94"),
        ("Max LA Volume/BSA (mL/m²)", "16 - 56" if sk=="H" else "18 - 54")
    ])

elif seleccion == "AI por Edad":
    st.caption("Calculado mediante volumen biplano por área longitud.")
    st.caption(f"Filtro etario activo: {edad} años")
    if bracket == "<20":
        datos_mostrar.extend([
            ("Max LA Volume (mL)", "Datos no disponibles para la edad"),
            ("Max LA Volume/BSA (mL/m²)", "Datos no disponibles para la edad")
        ])
    else:
        ai_age = {
            "H": {"20-29": ("40-103", "22-54"), "30-39": ("33-107", "19-54"), "40-49": ("34-108", "20-54"), "50-59": ("28-112", "17-55"), "60-69": ("23-112", "15-57"), ">=70": ("24-115", "13-59")},
            "M": {"20-29": ("30-89", "21-53"), "30-39": ("34-85", "22-50"), "40-49": ("29-95", "20-53"), "50-59": ("24-94", "17-52"), "60-69": ("21-96", "15-55"), ">=70": ("24-102", "15-58")}
        }
        vals = ai_age[sk][bracket]
        datos_mostrar.extend([
            ("Max LA Volume (mL)", vals[0]),
            ("Max LA Volume/BSA (mL/m²)", vals[1])
        ])

elif seleccion == "AI (Área y Diámetros)":
    datos_mostrar.extend([
        ("Max LA Area 2ch (cm²)", "12 - 29" if sk=="H" else "9 - 27"),
        ("Max LA Area 2ch/BSA (cm²/m²)", "7 - 16" if sk=="H" else "6 - 16"),
        ("Max LA Area 4ch (cm²)", "13 - 29" if sk=="H" else "11 - 27"),
        ("Max LA Area 4ch/BSA (cm²/m²)", "7 - 15" if sk=="H" else "7 - 16")
    ])

elif seleccion == "Aurícula Derecha (AD)":
    st.caption("Extrayendo valores de: Single-plane area-length method (4ch).")
    datos_mostrar.extend([
        ("Max RA Volume (mL)", "14 - 125" if sk=="H" else "20 - 95"),
        ("Max RA Volume/BSA (mL/m²)", "11 - 64" if sk=="H" else "15 - 56")
    ])

elif seleccion == "AD por Edad":
    st.caption(f"Filtro etario activo: {edad} años")
    if bracket == "<20":
        datos_mostrar.extend([
            ("Max RA Volume (mL)", "Datos no disponibles para la edad"),
            ("Max RA Volume/BSA (mL/m²)", "Datos no disponibles para la edad")
        ])
    else:
        ad_age = {
            "H": {"20-29": ("18-118", "13-59"), "30-39": ("25-114", "17-57"), "40-49": ("16-131", "11-65"), "50-59": ("18-127", "12-62"), "60-69": ("7-129", "8-66"), ">=70": ("35-140", "17-71")},
            "M": {"20-29": ("29-81", "19-49"), "30-39": ("30-81", "20-48"), "40-49": ("20-97", "16-55"), "50-59": ("21-98", "15-55"), "60-69": ("22-99", "15-57"), ">=70": ("30-105", "17-61")}
        }
        vals = ad_age[sk][bracket]
        datos_mostrar.extend([
            ("Max RA Volume (mL)", vals[0]),
            ("Max RA Volume/BSA (mL/m²)", vals[1])
        ])

elif seleccion == "AD (Área y Diámetros)":
    datos_mostrar.extend([
        ("Max RA Area 4ch (cm²)", "11 - 31" if sk=="H" else "11 - 25"),
        ("Max RA Area 4ch/BSA (cm²/m²)", "6 - 16" if sk=="H" else "6 - 15")
    ])

elif seleccion == "Aorta (Diámetros)":
    br_ao = get_age_bracket(edad, "aorta_65")
    st.caption(f"Aplicando filtro etario global y por edad ({br_ao} años)")
    
    # El valor general siempre se muestra
    datos_mostrar.append(("Ascending Aorta (mm)", "19 - 35" if sk=="H" else "18 - 33"))
    
    # Manejo del límite de edad específico para la aorta (no hay datos fuera de 45-84)
    if br_ao in ["<45", ">=85"]:
        datos_mostrar.extend([
            ("Ascending Aorta (Edad) (mm)", "Datos no disponibles para la edad"),
            ("Ascending Aorta/BSA (mm/m²)", "Datos no disponibles para la edad")
        ])
    else:
        datos_mostrar.extend([
            ("Ascending Aorta (Edad) (mm)", "27 - 37" if sk=="H" else "25 - 34"),
            ("Ascending Aorta/BSA (mm/m²)", "13 - 20" if sk=="H" else "14 - 21")
        ])

elif seleccion == "Raíz de Aorta por Edad":
    st.caption(f"Filtro etario activo: {edad} años")
    if bracket == "<20":
        datos_mostrar.extend([
            ("Aortic Sinus Diameter (mm)", "Datos no disponibles para la edad"),
            ("Aortic Sinus Diameter/BSA (mm/m²)", "Datos no disponibles para la edad")
        ])
    else:
        raiz_data = {
            "H": {"20-29": (30.1, 3.0, 15.9, 2.1), "30-39": (30.7, 3.2, 15.6, 1.8), "40-49": (32.0, 3.2, 16.3, 1.8), "50-59": (31.4, 4.0, 17.7, 2.1), "60-69": (33.3, 3.4, 17.7, 1.8), ">=70": (35.1, 3.7, 18.0, 1.2)},
            "M": {"20-29": (25.0, 3.5, 15.1, 1.9), "30-39": (25.3, 2.9, 15.7, 1.8), "40-49": (29.2, 3.8, 17.9, 2.1), "50-59": (28.0, 2.8, 17.1, 1.5), "60-69": (28.6, 3.9, 17.8, 1.8), ">=70": (30.2, 2.0, 18.2, 0.9)}
        }
        r = raiz_data[sk][bracket]
        datos_mostrar.extend([
            ("Aortic Sinus Diameter (mm)", format_range(r[0], r[1])),
            ("Aortic Sinus Diameter/BSA (mm/m²)", format_range(r[2], r[3]))
        ])

elif seleccion == "Senos de Valsalva":
    st.caption(f"Filtro etario activo: {edad} años")
    if bracket == "<20":
        datos_mostrar.extend([
            ("Aortic Sinus Cusp-Comm (mm)", "Datos no disponibles para la edad"),
            ("Aortic Sinus Cusp-Comm/BSA (mm/m²)", "Datos no disponibles para la edad")
        ])
    else:
        senos_data = {
            "H": {"20-29": (30.4, 3.3, 15.6, 1.7), "30-39": (29.7, 3.5, 15.1, 1.6), "40-49": (31.6, 1.6, 15.3, 1.0), "50-59": (32.7, 4.8, 16.6, 1.9), "60-69": (33.5, 2.3, 17.2, 1.7), ">=70": (33.9, 3.0, 17.4, 1.2)},
            "M": {"20-29": (26.3, 3.9, 15.3, 2.0), "30-39": (26.8, 2.8, 16.4, 1.3), "40-49": (30.0, 2.1, 16.8, 2.3), "50-59": (28.4, 1.8, 17.2, 1.4), "60-69": (29.5, 2.0, 17.1, 1.4), ">=70": (29.6, 1.4, 17.8, 0.9)}
        }
        s = senos_data[sk][bracket]
        datos_mostrar.extend([
            ("Aortic Sinus Cusp-Comm (mm)", format_range(s[0], s[1])),
            ("Aortic Sinus Cusp-Comm/BSA (mm/m²)", format_range(s[2], s[3]))
        ])

elif seleccion == "Arteria Pulmonar":
    # Lógica actualizada para extraer Diámetro Sistólico y Diastólico de MPA (Main Pulmonary Artery)
    st.caption(f"Filtro etario activo: {edad} años (Calculados Mean ± 2SD)")
    if bracket == "<20":
        datos_mostrar.extend([
            ("MPA Systolic Diameter (mm)", "Datos no disponibles para la edad"),
            ("MPA Diastolic Diameter (mm)", "Datos no disponibles para la edad")
        ])
    else:
        pulm_data = {
            "H": {
                "20-29": (28.3, 1.8, 22.4, 1.8),
                "30-39": (27.3, 2.7, 21.9, 1.8),
                "40-49": (28.2, 3.1, 23.5, 2.8),
                "50-59": (27.0, 2.7, 22.9, 3.0),
                "60-69": (26.5, 2.2, 23.3, 2.1),
                ">=70": (27.1, 2.7, 23.6, 2.6)
            },
            "M": {
                "20-29": (26.4, 3.3, 21.6, 2.9),
                "30-39": (25.5, 2.8, 20.4, 2.0),
                "40-49": (26.5, 1.6, 21.5, 1.6),
                "50-59": (24.4, 2.7, 20.7, 2.1),
                "60-69": (25.0, 2.7, 21.6, 2.0),
                ">=70": (24.0, 1.9, 21.4, 1.9)
            }
        }
        p = pulm_data[sk][bracket]
        datos_mostrar.extend([
            ("MPA Systolic Diameter (mm)", format_range(p[0], p[1])),
            ("MPA Diastolic Diameter (mm)", format_range(p[2], p[3]))
        ])

elif seleccion == "Atletas VI":
    st.caption("Comparativa: Atletas Regulares vs Elite")
    datos_mostrar.extend([
        ("Regular: LVEDV/BSA (mL/m²)", "97 - 149" if sk=="H" else "79 - 135"),
        ("Regular: LVESV/BSA (mL/m²)", "35 - 71" if sk=="H" else "32 - 64"),
        ("Regular: LVM/BSA (g/m²)", "40 - 84" if sk=="H" else "28 - 64"),
        ("Regular: LVEF (%)", "47 - 67" if sk=="H" else "47 - 63"),
        ("Elite: LVEDV/BSA (mL/m²)", "95 - 163" if sk=="H" else "79 - 135"),
        ("Elite: LVESV/BSA (mL/m²)", "36 - 80" if sk=="H" else "24 - 68"),
        ("Elite: LVM/BSA (g/m²)", "43 - 95" if sk=="H" else "34 - 66"),
        ("Elite: LVEF (%)", "45 - 65" if sk=="H" else "44 - 72")
    ])

elif seleccion == "Atletas VD":
    st.caption("Comparativa: Atletas Regulares vs Elite")
    datos_mostrar.extend([
        ("Regular: RVEDV/BSA (mL/m²)", "104 - 168" if sk=="H" else "85 - 145"),
        ("Regular: RVESV/BSA (mL/m²)", "42 - 90" if sk=="H" else "39 - 75"),
        ("Regular: RVEF (%)", "43 - 59" if sk=="H" else "43 - 59"),
        ("Elite: RVEDV/BSA (mL/m²)", "104 - 184" if sk=="H" else "84 - 152"),
        ("Elite: RVESV/BSA (mL/m²)", "47 - 99" if sk=="H" else "30 - 82"),
        ("Elite: RVEF (%)", "42 - 58" if sk=="H" else "39 - 67")
    ])

elif seleccion == "Mapas Tisulares (T1/T2/ECV)":
    datos_mostrar.extend([
        ("T1 Nativo (ms)", "956 - 1098 (GE 1.5T)"),
        ("T2 Nativo (ms)", "46 - 58 (GE 1.5T)"),
        ("ECV (%)", "21.9 - 32.7 (Siemens 1.5T)")
    ])

# Renderizar las métricas
if datos_mostrar:
    mostrar_grid(datos_mostrar)

# --- IMAGEN DE REFERENCIA ---
st.divider()

if seleccion == "Senos de Valsalva":
    col_img1, col_img2 = st.columns([1, 2])
    with col_img1:
        st.markdown("**Diagrama de Referencia**")
        if os.path.exists("Senos de Valsalva.jpg"):
            st.image("Senos de Valsalva.jpg", use_container_width=True)
    with col_img2:
        st.markdown(f"**Anexo Visual:** {seleccion}")
        f_name = mapping[seleccion]
        if os.path.exists(f_name):
            st.image(f_name, use_container_width=True)

elif seleccion in ["Diámetro Anillo Mitral", "Diámetro Anillo Tricuspídeo"]:
    col_img1, col_img2 = st.columns([1, 2])
    with col_img1:
        st.markdown("**Diagrama de Referencia**")
        if os.path.exists("Anillo mitral y tricuspideo.jpg"):
            st.image("Anillo mitral y tricuspideo.jpg", use_container_width=True)
    with col_img2:
        st.markdown(f"**Anexo Visual:** {seleccion}")
        f_name = mapping[seleccion]
        if os.path.exists(f_name):
            st.image(f_name, use_container_width=True)

elif seleccion == "Valvulopatía":
    st.markdown(f"**Anexo Visual:** {seleccion}")
    f_name = mapping[seleccion]
    if os.path.exists(f_name):
        st.image(f_name, width=1000)

else:
    f_name = mapping.get(seleccion)
    if f_name and os.path.exists(f_name):
        st.markdown(f"**Anexo Visual:** {seleccion}")
        img_width = 800 if "Aorta" in seleccion or "Pulmonar" in seleccion or "Atletas" in seleccion else 1000
        st.image(f_name, width=img_width)