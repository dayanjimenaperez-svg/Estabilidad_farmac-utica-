
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ==================================================
# CONFIGURACION GENERAL
# ==================================================

st.set_page_config(
    page_title="Análisis cinético y estabilidad",
    page_icon="🧪",
    layout="wide"
)
# ==================================================
# DISEÑO DE TODA LA PAGINA - ROSADO PASTEL
# ==================================================

st.markdown("""
<style>

/* Fondo de toda la pagina */
.stApp,
[data-testid="stAppViewContainer"] {
    background-color: #FFF0F5 !important;
}

/* Fondo del contenido principal */
[data-testid="stMain"] {
    background-color: #FFF0F5 !important;
}

/* Encabezado */
[data-testid="stHeader"] {
    background-color: #FCE4EC !important;
}

/* Titulos */
h1, h2, h3, h4 {
    color: #994D70 !important;
}

/* Texto general */
.stApp p,
.stApp label {
    color: #65465A;
}

/* Barra lateral */
[data-testid="stSidebar"] {
    background-color: #F8DCE7 !important;
}

/* Botones */
.stButton button {
    background-color: #D98EAF !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: bold !important;
}

/* Botones al pasar el cursor */
.stButton button:hover {
    background-color: #BD6F94 !important;
}

/* Cuadros de informacion */
[data-testid="stAlert"] {
    background-color: #FCE4EC !important;
    border-radius: 12px !important;
}

/* Contenedores */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: #E8B8CC !important;
}

/* Campos de entrada */
.stNumberInput input,
.stTextInput input {
    background-color: #FFF9FB !important;
}

/* Selectores */
.stSelectbox div[data-baseweb="select"] {
    background-color: #FFF9FB !important;
}

/* Separadores */
hr {
    border-color: #E8B8CC !important;
}

</style>
""", unsafe_allow_html=True)

st.title("🧪 ANÁLISIS CINÉTICO Y ESTABILIDAD")

st.markdown(
    "### 1. Determinación automática del orden cinético"
)

st.write(
    "Ingrese los datos experimentales de tiempo y concentración. "
    "El programa evaluará los ordenes cero, uno y dos mediante "
    "el método integral."
)

# ==================================================
# SELECCION DE UNIDADES
# ==================================================

st.divider()
st.subheader("Unidades de medición")

unidades_tiempo = {
    "Segundos (s)": 1,
    "Minutos (min)": 60,
    "Horas (h)": 3600,
    "Días (d)": 86400,
    "Semanas (sem)": 604800
}

# Factores expresados en mg/L
unidades_concentración = {
    "g/L": 1000,
    "mg/L": 1,
    "ug/L": 0.001,
    "mg/mL": 1000,
    "ug/mL": 1,
    "g/mL": 1000000,
    "kg/m3": 1000
}

col1, col2 = st.columns(2)

with col1:

    st.markdown("**UNIDADES DE TIEMPO**")

    unidad_t_entrada = st.selectbox(
        "Unidad original del tiempo",
        list(unidades_tiempo.keys()),
        index=3
    )

    unidad_t = st.selectbox(
        "Convertir tiempo a",
        list(unidades_tiempo.keys()),
        index=3
    )

with col2:

    st.markdown("**UNIDADES DE CONCENTRACIÓN**")

    unidad_c_entrada = st.selectbox(
        "Unidad original de concentración",
        list(unidades_concentración.keys()),
        index=1
    )

    unidad_c = st.selectbox(
        "Convertir concentración a",
        list(unidades_concentración.keys()),
        index=1
    )


# ==================================================
# INGRESO DE DATOS EXPERIMENTALES
# ==================================================

st.divider()
st.subheader("Datos experimentales")

st.info(
    "Puedes modificar los datos de ejemplo, agregar filas "
    "o eliminar las que no necesites."
)

datos_iniciales = pd.DataFrame({
    "Tiempo": [0.000, 1.000, 2.000, 3.000, 4.000],
    "Concentración": [100.000, 82.000, 67.000, 55.000, 45.000]
}).astype({
    "Tiempo": "float64",
    "Concentración": "float64"
})

datos_editados = st.data_editor(
    datos_iniciales,
    num_rows="dynamic",
    use_container_width=True,
    key="tabla_experimental_corregida",
    column_config={

        "Tiempo": st.column_config.NumberColumn(
            "Tiempo",
            format="%.4f",
            step=0.0001
        ),

        "Concentración": st.column_config.NumberColumn(
            "Concentración",
            format="%.4f",
            step=0.0001
        )
    }
)


# ==================================================
# ANALISIS CINETICO
# ==================================================

if st.button("ANALIZAR ORDEN CINÉTICO", type="primary"):

    # Recuperar los datos de la tabla editable
    datos = datos_editados.copy()

    # Eliminar solamente las filas completamente vacias
    datos = datos.dropna(
        subset=["Tiempo", "Concentración"],
        how="all"
    ).copy()

    # Reiniciar los indices
    datos = datos.reset_index(drop=True)

    # Convertir los datos a valores numericos
    datos["Tiempo"] = pd.to_numeric(
        datos["Tiempo"],
        errors="coerce"
    )

    datos["Concentración"] = pd.to_numeric(
        datos["Concentración"],
        errors="coerce"
    )

    # ==================================================
    # VALIDACION DE DATOS
    # ==================================================

    if datos.empty:

        st.error(
            "Debes ingresar datos experimentales."
        )

    elif datos.isna().any().any():

        st.error(
            "Hay celdas vacías o valores no numéricos. "
            "Revisa la tabla experimental."
        )

    elif (
        not np.isfinite(datos["Tiempo"]).all()
        or not np.isfinite(datos["Concentración"]).all()
    ):

        st.error(
            "Los datos deben ser valores finitos."
        )

    elif len(datos) < 3:

        st.error(
            "Se necesitan al menos tres datos experimentales."
        )

    elif (datos["Concentración"] <= 0).any():

        valores_invalidos = datos.loc[
            datos["Concentración"] <= 0,
            ["Tiempo", "Concentración"]
        ]

        st.error(
            "Hay concentraciones iguales o menores que cero."
        )

        st.dataframe(
            valores_invalidos,
            use_container_width=True
        )

        st.warning(
            "Todas las concentraciones deben ser positivas "
            "para calcular el logaritmo natural."
        )

    elif datos["Tiempo"].nunique() < 3:

        st.error(
            "Se necesitan al menos tres tiempos diferentes."
        )

    else:

        # ==================================================
        # ORGANIZACION DE LOS DATOS
        # ==================================================

        datos = datos.sort_values(
            "Tiempo"
        )

        t_original = datos["Tiempo"].to_numpy(
            dtype=float
        )

        c_original = datos["Concentración"].to_numpy(
            dtype=float
        )

        # ==================================================
        # CONVERSION AUTOMATICA DE UNIDADES
        # ==================================================

        t = (
            t_original
            * unidades_tiempo[unidad_t_entrada]
            / unidades_tiempo[unidad_t]
        )

        c = (
            c_original
            * unidades_concentración[unidad_c_entrada]
            / unidades_concentración[unidad_c]
        )

        # Comprobar que las conversiones sean validas
        if (
            not np.isfinite(t).all()
            or not np.isfinite(c).all()
            or (c <= 0).any()
        ):

            st.error(
                "Error durante la conversión de unidades. "
                "Revisa los valores ingresados."
            )

        else:

            st.success(
                "Datos validados y unidades convertidas correctamente."
            )

            st.write(
                "### Datos después de la conversión"
            )

            tabla_convertida = pd.DataFrame({

                f"Tiempo ({unidad_t})": t,

                f"Concentración ({unidad_c})": c

            })

            st.dataframe(
                tabla_convertida.style.format("{:.4f}"),
                use_container_width=True
            )

            # ==================================================
            # REGRESIONES DEL METODO INTEGRAL
            # ==================================================

            modelos = [

                {
                    "orden": "Orden cero",
                    "transformación": "C",
                    "y": c,
                    "signo": -1
                },

                {
                    "orden": "Orden uno",
                    "transformación": "ln(C)",
                    "y": np.log(c),
                    "signo": -1
                },

                {
                    "orden": "Orden dos",
                    "transformación": "1/C",
                    "y": 1 / c,
                    "signo": 1
                }

            ]

            resultados = []

            for modelo in modelos:

                y = modelo["y"]

                # Regresion lineal
                pendiente, intercepto = np.polyfit(
                    t,
                    y,
                    1
                )

                # Prediccion del modelo
                prediccion = (
                    pendiente * t + intercepto
                )

                # Suma de cuadrados residuales
                ss_res = np.sum(
                    (y - prediccion) ** 2
                )

                # Suma total de cuadrados
                ss_tot = np.sum(
                    (y - np.mean(y)) ** 2
                )

                # Coeficiente de determinacion
                r2 = (
                    1 - ss_res / ss_tot
                    if ss_tot > 0
                    else np.nan
                )

                # Constante cinetica
                k = modelo["signo"] * pendiente

                resultados.append({

                    "Orden": modelo["orden"],

                    "Transformación": modelo["transformación"],

                    "Pendiente": pendiente,

                    "Intercepto": intercepto,

                    "k": k,

                    "R2": r2,

                    "y": y,

                    "prediccion": prediccion

                })

            # ==================================================
            # TABLA COMPARATIVA DE RESULTADOS
            # ==================================================

            st.divider()

            st.subheader(
                "2. Resultados de las regresiones"
            )

            resumen = pd.DataFrame([

                {
                    "Orden": m["Orden"],

                    "Transformación": m["Transformación"],

                    "Pendiente": m["Pendiente"],

                    "Intercepto": m["Intercepto"],

                    "Constante k": m["k"],

                    "R2": m["R2"]

                }

                for m in resultados

            ])

            st.dataframe(
                resumen.style.format({

                    "Pendiente": "{:.4f}",

                    "Intercepto": "{:.4f}",

                    "Constante k": "{:.4g}",

                    "R2": "{:.4f}"

                }),
                use_container_width=True
            )
# ==================================================
            # GRAFICAS DE LOS TRES MODELOS
            # ==================================================

            st.divider()

            st.subheader(
                "3. Gráficas de los modelos cinéticos"
            )

            for m in resultados:

                fig = go.Figure()

                # Datos experimentales
                fig.add_trace(
                    go.Scatter(

                        x=t,

                        y=m["y"],

                        mode="lines+markers",

                        name="Datos experimentales"

                    )
                )

                # Regresion lineal
                fig.add_trace(
                    go.Scatter(

                        x=t,

                        y=m["prediccion"],

                        mode="lines",

                        name="Regresión lineal"

                    )
                )

                fig.update_layout(

                    title=(
                        f"{m['Orden']} - "
                        f"R2 = {m['R2']:.4f}"
                    ),

                    xaxis_title=f"Tiempo ({unidad_t})",

                    yaxis_title=m["Transformación"],

                    template="plotly_white"

                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )
            # ==================================================
            # SELECCION DEL MEJOR MODELO
            # ==================================================

            st.divider()

            st.subheader(
                "4. Orden cinético seleccionado"
            )

            validos = [

                m for m in resultados

                if (
                    np.isfinite(m["R2"])
                    and np.isfinite(m["k"])
                    and m["k"] > 0
                )

            ]

            if not validos:

                st.warning(
                    "No se encontró un modelo con R2 válido "
                    "y constante cinética positiva."
                )

            else:

                mejor = max(
                    validos,
                    key=lambda m: m["R2"]
                )

                # Unidades de la constante cinética

                if mejor["Orden"] == "Orden cero":

                    unidad_k = (
                        f"{unidad_c}/{unidad_t}"
                    )

                elif mejor["Orden"] == "Orden uno":

                    unidad_k = (
                        f"1/{unidad_t}"
                    )

                else:

                    unidad_k = (
                        f"1/({unidad_c}·{unidad_t})"
                    )

                st.success(
                    f"El orden cinético seleccionado es: "
                    f"{mejor['Orden']}"
                )

                st.metric(
    "Coeficiente R2",
    f"{mejor['R2']:.4f}"
)

                st.write(
                    f"**Modelo:** {mejor['Transformación']}"
                )

                st.write(
                    f"**Ecuación:** y = "
                    f"{mejor['Pendiente']:.4f}t "
                    f"+ {mejor['Intercepto']:.4f}"
                )


                # ==================================================
                # CALCULO DE k, t50, t98, t95 y t90
                # ==================================================

                st.divider()

                st.subheader(
                    "5. Constante cinética y tiempos característicos"
                )

                # Concentración inicial experimental
                C0 = float(c[0])

                # Constante cinética del orden seleccionado
                k_calculada = float(mejor["k"])

                if k_calculada <= 0 or C0 <= 0:

                    st.error(
                        "No es posible calcular los tiempos. "
                        "La constante k y C0 deben ser positivas."
                    )

                else:

                    # Fracción de concentración que permanece
                    fracciones = {
                        "t50": 0.50,
                        "t98": 0.98,
                        "t95": 0.95,
                        "t90": 0.90
                    }

                    tiempos = {}

                    # Ecuaciones segun el orden cinetico
                    for nombre, fraccion in fracciones.items():

                        if mejor["Orden"] == "Orden cero":

                            tiempo = (
                                C0 * (1 - fraccion)
                                / k_calculada
                            )

                        elif mejor["Orden"] == "Orden uno":

                            tiempo = (
                                -np.log(fraccion)
                                / k_calculada
                            )

                        elif mejor["Orden"] == "Orden dos":

                            tiempo = (
                                (1 / fraccion - 1)
                                / (k_calculada * C0)
                            )

                        tiempos[nombre] = tiempo

                    # Mostrar constante cinética
                    st.metric(
                        f"Constante cinética k ({unidad_k})",
                        f"{k_calculada:.4g}"
                    )

                    # Mostrar tiempos característicos
                    st.markdown("### Tiempos calculados")

                    columnas = st.columns(4)

                    for columna, (nombre, valor) in zip(
                        columnas,
                        tiempos.items()
                    ):

                        with columna:

                            st.metric(
                                nombre,
                                f"{valor:.4f} {unidad_t}"
                            )

                    # Tabla de resultados
                    tabla_tiempos = pd.DataFrame({

                        "Parámetro": [
                            "Constante cinética k",
                            "t50",
                            "t98",
                            "t95",
                            "t90"
                        ],

                        "Resultado": [
                            k_calculada,
                            tiempos["t50"],
                            tiempos["t98"],
                            tiempos["t95"],
                            tiempos["t90"]
                        ],

                        "Unidad": [
                            unidad_k,
                            unidad_t,
                            unidad_t,
                            unidad_t,
                            unidad_t
                        ]

                    })

                    st.markdown(
                        "### Resumen de resultados cinéticos"
                    )

                    st.dataframe(
                        tabla_tiempos.style.format({
                            "Resultado": "{:.4g}"
                        }),
                        width="stretch"
                    )

                    # Descargar resultados
                    csv_tiempos = tabla_tiempos.to_csv(
                        index=False
                    ).encode("utf-8-sig")

                    st.download_button(
                        "Descargar tiempos característicos",
                        data=csv_tiempos,
                        file_name="tiempos_caracteristicos.csv",
                        mime="text/csv",
                        key="descargar_tiempos_caracteristicos"
                    )
            
# ==================================================
# MODULO 2: ANALISIS DE ARRHENIUS
# ==================================================

st.divider()

st.title("🌡️ ANÁLISIS DE ARRHENIUS")

st.markdown("""
### 6. Determinación de la energía de activación

Ingrese las constantes cinéticas obtenidas a diferentes
temperaturas para determinar los parámetros de Arrhenius.
""")


st.write(
    "Ingresa las constantes cinéticas (k) obtenidas "
    "a diferentes temperaturas para calcular la energía "
    "de activación y el factor preexponencial."
)

# ------------------------------------------------------------
# 1. ECUACIONES
# ------------------------------------------------------------

st.subheader("Ecuaciones utilizadas")

st.latex(r"k = A e^{-\frac{Ea}{RT}}")

st.write("Ecuación linealizada:")

st.latex(
    r"\ln(k) = -\frac{Ea}{R}\left(\frac{1}{T}\right) + \ln(A)"
)

st.write(
    "Donde la pendiente corresponde a -Ea/R "
    "y el intercepto corresponde a ln(A)."
)

# ------------------------------------------------------------
# 2. INGRESO DE DATOS
# ------------------------------------------------------------

st.subheader("Ingreso de datos experimentales")

unidad_temperatura = st.selectbox(
    "Unidad de temperatura:",
    ["°C", "K"],
    key="unidad_temp_arrhenius"
)

datos_iniciales = pd.DataFrame({
    "Temperatura": [20.0, 30.0, 40.0],
    "k": [0.010, 0.020, 0.040]
})

datos_arrhenius = st.data_editor(
    datos_iniciales,
    num_rows="dynamic",
    use_container_width=True,
    key="tabla_datos_arrhenius"
)

st.caption(
    "Puedes modificar los valores de ejemplo, agregar filas "
    "o eliminar datos. Todas las constantes k deben ser positivas "
    "y estar expresadas en las mismas unidades."
)

# ------------------------------------------------------------
# 3. CÁLCULOS
# ------------------------------------------------------------

if st.button("CALCULAR ENERGÍA DE ACTIVACIÓN",
             key="calcular_arrhenius"):

    datos = datos_arrhenius.copy()

    # Convertir los datos a valores numéricos
    datos["Temperatura"] = pd.to_numeric(
        datos["Temperatura"], errors="coerce"
    )

    datos["k"] = pd.to_numeric(
        datos["k"], errors="coerce"
    )

    # Eliminar filas vacías
    datos = datos.dropna(subset=["Temperatura", "k"])

    # Validaciones
    if len(datos) < 3:

        st.error(
            "Debes ingresar al menos tres pares de datos "
            "de temperatura y constante cinética."
        )

    elif not np.isfinite(datos[["Temperatura", "k"]].to_numpy()).all():

        st.error("Los datos deben ser valores numéricos finitos.")

    elif (datos["k"] <= 0).any():

        st.error("Todas las constantes cinéticas k deben ser positivas.")

    else:

        # ----------------------------------------------------
        # 4. CONVERSIÓN DE TEMPERATURA
        # ----------------------------------------------------

        if unidad_temperatura == "°C":
            temperatura_K = datos["Temperatura"] + 273.15
        else:
            temperatura_K = datos["Temperatura"]

        if (temperatura_K <= 0).any():

            st.error(
                "La temperatura en Kelvin debe ser mayor que cero."
            )

        elif temperatura_K.nunique() < 3:

            st.error(
                "Debes ingresar al menos tres temperaturas diferentes."
            )

        else:

            # ------------------------------------------------
            # 5. CÁLCULO DE 1/T Y LN(K)
            # ------------------------------------------------

            datos["Temperatura (K)"] = temperatura_K
            datos["1/T (K⁻¹)"] = 1 / temperatura_K
            datos["ln(k)"] = np.log(datos["k"])

            # ------------------------------------------------
            # 6. REGRESIÓN LINEAL
            # ------------------------------------------------

            x = datos["1/T (K⁻¹)"].to_numpy()
            y = datos["ln(k)"].to_numpy()

            pendiente, intercepto = np.polyfit(x, y, 1)

            y_estimado = pendiente * x + intercepto

            # Cálculo de R²
            ss_res = np.sum((y - y_estimado) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)

            if ss_tot == 0:
                R2 = 0
            else:
                R2 = 1 - (ss_res / ss_tot)

            # ------------------------------------------------
            # 7. ENERGÍA DE ACTIVACIÓN Y FACTOR A
            # ------------------------------------------------

            R_ARRHENIUS = 8.314462618

            # Ea = -pendiente * R
            Ea = -pendiente * R_ARRHENIUS

            # A = e elevado al intercepto
            with np.errstate(over="ignore", under="ignore"):
                A = np.exp(intercepto)

            # Validar resultados
            if not np.isfinite(Ea) or not np.isfinite(A) or A <= 0:

                st.error(
                    "No fue posible calcular resultados válidos. "
                    "Revisa los valores experimentales."
                )

            else:
                st.session_state["Ea_arrhenius"] = Ea
                st.session_state["A_arrhenius"] = A
                st.session_state["R2_arrhenius"] = R2
                # --------------------------------------------
                # 8. TABLA DE RESULTADOS
                # --------------------------------------------

                st.subheader("Resultados experimentales")

                tabla_resultados = datos[
                    [
                        "Temperatura",
                        "Temperatura (K)",
                        "k",
                        "1/T (K⁻¹)",
                        "ln(k)"
                    ]
                ].copy()

                tabla_mostrar = tabla_resultados.copy()

                tabla_mostrar["Temperatura"] = (
                    tabla_mostrar["Temperatura"].map(lambda v: f"{v:.4f}")
                )

                tabla_mostrar["Temperatura (K)"] = (
                    tabla_mostrar["Temperatura (K)"].map(lambda v: f"{v:.4f}")
                )

                tabla_mostrar["k"] = (
                    tabla_mostrar["k"].map(lambda v: f"{v:.4e}")
                )

                tabla_mostrar["1/T (K⁻¹)"] = (
                    tabla_mostrar["1/T (K⁻¹)"].map(lambda v: f"{v:.8f}")
                )

                tabla_mostrar["ln(k)"] = (
                    tabla_mostrar["ln(k)"].map(lambda v: f"{v:.4f}")
                )

                st.dataframe(
                    tabla_mostrar,
                    use_container_width=True,
                    hide_index=True
                )

                # --------------------------------------------
                # 9. GRÁFICA DE ARRHENIUS
                # --------------------------------------------

                st.subheader("Gráfica de Arrhenius")

                x_linea = np.linspace(min(x), max(x), 100)
                y_linea = pendiente * x_linea + intercepto

                fig_arrhenius = go.Figure()

                fig_arrhenius.add_trace(
                    go.Scatter(
                        x=x,
                        y=y,
                        mode="lines+markers",
                        name="Datos experimentales",
                        marker=dict(size=10)
                    )
                )

                fig_arrhenius.add_trace(
                    go.Scatter(
                        x=x_linea,
                        y=y_linea,
                        mode="lines",
                        name="Regresión lineal"
                    )
                )

                fig_arrhenius.update_layout(
                    title="Gráfica de Arrhenius",
                    xaxis_title="1/T (K⁻¹)",
                    yaxis_title="ln(k)",
                    template="plotly_white"
                )

                st.plotly_chart(
                    fig_arrhenius,
                    use_container_width=True
                )

                # --------------------------------------------
                # 10. RESULTADOS CINÉTICOS
                # --------------------------------------------

                st.subheader("Parámetros cinéticos")

                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "Energía de activación (Ea)",
                        f"{Ea / 1000:.4f} kJ/mol"
                    )

                with col2:
                    st.metric(
                        "Factor preexponencial (A)",
                        f"{A:.4e}"
                    )

                col3, col4, col5 = st.columns(3)

                with col3:
                    st.metric("Pendiente", f"{pendiente:.4f}")

                with col4:
                    st.metric("Intercepto", f"{intercepto:.4f}")

                with col5:
                    st.metric("R²", f"{R2:.4f}")

                # --------------------------------------------
                # 11. ECUACIÓN LINEALIZADA
                # --------------------------------------------

                st.subheader("Ecuación linealizada obtenida")

                st.latex(
                    rf"\ln(k) = ({pendiente:.6f})"
                    rf"\left(\frac{{1}}{{T}}\right)"
                    rf" + ({intercepto:.6f})"
                )

                st.write(
                    f"**Energía de activación:** "
                    f"{Ea / 1000:.4f} kJ/mol"
                )

                st.write(
                    f"**Factor preexponencial:** {A:.4e}"
                )

            
                # ==================================================
                # DESCARGA DE RESULTADOS
                # ==================================================

                st.divider()

                st.subheader(
                    "11. Exportar resultados de Arrhenius"
                )

                csv_A = tabla_resultados.to_csv(
                    index=False
                ).encode("utf-8-sig")

                st.download_button(
                    "Descargar resultados de Arrhenius",
                    data=csv_A,
                    file_name="resultados_arrhenius.csv",
                    mime="text/csv",
                    key="descargar_arrhenius"
                )
# ============================================================
# PREDICCIÓN DE K Y CAMBIOS EN TIEMPOS DE VIDA ÚTIL
# ============================================================

st.divider()

st.header("PREDICCIÓN DE ESTABILIDAD A DIFERENTES TEMPERATURAS")

st.write(
    "Esta herramienta permite estimar cómo cambia la constante "
    "cinética y los tiempos de degradación del producto cuando "
    "se modifica la temperatura."
)

# ------------------------------------------------------------
# 1. VERIFICAR DATOS DE ARRHENIUS
# ------------------------------------------------------------

if (
    "Ea_arrhenius" not in st.session_state
    or "A_arrhenius" not in st.session_state
):

    st.warning(
        "Primero debes ejecutar el análisis de Arrhenius "
        "para obtener la energía de activación y el factor A."
    )

else:

    Ea_pred = st.session_state["Ea_arrhenius"]
    A_pred = st.session_state["A_arrhenius"]
    R_pred = 8.314462618

    # --------------------------------------------------------
    # 2. INGRESO DE TEMPERATURAS
    # --------------------------------------------------------

    st.subheader("Temperaturas de evaluación")

    unidad_pred = st.selectbox(
        "Unidad de temperatura:",
        ["°C", "K"],
        key="unidad_prediccion"
    )

    temperaturas_iniciales = pd.DataFrame({
        "Temperatura": [20.0, 30.0, 40.0, 50.0, 60.0]
    })

    temperaturas_usuario = st.data_editor(
        temperaturas_iniciales,
        num_rows="dynamic",
        use_container_width=True,
        key="tabla_temperaturas_prediccion"
    )

    # --------------------------------------------------------
    # 3. SELECCIÓN DEL ORDEN CINÉTICO
    # --------------------------------------------------------

    st.subheader("Parámetros de degradación")

    orden_pred = st.selectbox(
        "Selecciona el orden cinético de la reacción:",
        [
            "Orden cero",
            "Primer orden",
            "Segundo orden"
        ],
        key="orden_prediccion"
    )

    C0_pred = st.number_input(
        "Concentración inicial (C₀):",
        min_value=0.000001,
        value=100.0,
        step=1.0,
        key="concentracion_prediccion"
    )

    st.caption(
        "La concentración inicial debe expresarse en una unidad "
        "compatible con la constante cinética k."
    )

    # --------------------------------------------------------
    # 4. BOTÓN DE CÁLCULO
    # --------------------------------------------------------

    if st.button(
        "CALCULAR PREDICCIÓN DE ESTABILIDAD",
        key="boton_prediccion_estabilidad"
    ):

        temperaturas = temperaturas_usuario.copy()

        temperaturas["Temperatura"] = pd.to_numeric(
            temperaturas["Temperatura"],
            errors="coerce"
        )

        temperaturas = temperaturas.dropna()

        if temperaturas.empty:

            st.error("Debes ingresar temperaturas válidas.")

        elif len(temperaturas) < 1:

            st.error("Ingresa al menos una temperatura.")

        elif not np.isfinite(
            temperaturas["Temperatura"].to_numpy()
        ).all():

            st.error("Las temperaturas deben ser valores finitos.")

        else:

            # ------------------------------------------------
            # 5. CONVERSIÓN A KELVIN
            # ------------------------------------------------

            if unidad_pred == "°C":

                temperaturas["Temperatura (K)"] = (
                    temperaturas["Temperatura"] + 273.15
                )

            else:

                temperaturas["Temperatura (K)"] = (
                    temperaturas["Temperatura"]
                )

            if (temperaturas["Temperatura (K)"] <= 0).any():

                st.error(
                    "Todas las temperaturas deben ser mayores "
                    "que cero Kelvin."
                )

            elif C0_pred <= 0:

                st.error(
                    "La concentración inicial debe ser positiva."
                )

            else:

                # --------------------------------------------
                # 6. PREDICCIÓN DE LA CONSTANTE CINÉTICA
                # --------------------------------------------

                resultados_pred = []

                for _, fila in temperaturas.iterrows():

                    T = fila["Temperatura (K)"]

                    k_pred = A_pred * np.exp(
                        -Ea_pred / (R_pred * T)
                    )

                    if not np.isfinite(k_pred) or k_pred <= 0:
                        continue

                    # ----------------------------------------
                    # 7. CÁLCULO DE TIEMPOS DE VIDA ÚTIL
                    # ----------------------------------------

                    if orden_pred == "Orden cero":

                        t50 = (0.50 * C0_pred) / k_pred
                        t98 = (0.98 * C0_pred) / k_pred
                        t95 = (0.95 * C0_pred) / k_pred
                        t90 = (0.90 * C0_pred) / k_pred

                    elif orden_pred == "Primer orden":

                        t50 = np.log(2) / k_pred
                        t98 = np.log(50) / k_pred
                        t95 = np.log(20) / k_pred
                        t90 = np.log(10) / k_pred

                    else:

                        t50 = 1 / (k_pred * C0_pred)
                        t98 = 49 / (k_pred * C0_pred)
                        t95 = 19 / (k_pred * C0_pred)
                        t90 = 9 / (k_pred * C0_pred)

                    resultados_pred.append({
                        "Temperatura (°C)": (
                            fila["Temperatura"]
                            if unidad_pred == "°C"
                            else T - 273.15
                        ),
                        "Temperatura (K)": T,
                        "k estimada": k_pred,
                        "t50": t50,
                        "t98": t98,
                        "t95": t95,
                        "t90": t90
                    })

                # --------------------------------------------
                # 8. MOSTRAR RESULTADOS
                # --------------------------------------------

                if len(resultados_pred) == 0:

                    st.error(
                        "No fue posible obtener resultados válidos."
                    )

                else:

                    tabla_pred = pd.DataFrame(resultados_pred)

                    st.subheader(
                        "Resultados de predicción de estabilidad"
                    )

                    tabla_pred_mostrar = tabla_pred.copy()

                    for columna in tabla_pred_mostrar.columns:

                        tabla_pred_mostrar[columna] = (
                            tabla_pred_mostrar[columna].map(
                                lambda v: f"{v:.4e}"
                                if columna == "k estimada"
                                else f"{v:.4f}"
                            )
                        )

                    st.dataframe(
                        tabla_pred_mostrar,
                        use_container_width=True,
                        hide_index=True
                    )

                    st.caption(
                        "Los tiempos se expresan en las unidades "
                        "de tiempo correspondientes a la constante "
                        "cinética ingresada en el análisis."
                    )

                    # ----------------------------------------
                    # 9. GRÁFICA DE CONSTANTE CINÉTICA
                    # ----------------------------------------

                    st.subheader(
                        "Comportamiento de k según la temperatura"
                    )

                    fig_k = go.Figure()

                    fig_k.add_trace(
                        go.Scatter(
                            x=tabla_pred["Temperatura (°C)"],
                            y=tabla_pred["k estimada"],
                            mode="lines+markers",
                            name="k estimada"
                        )
                    )

                    fig_k.update_layout(
                        xaxis_title="Temperatura (°C)",
                        yaxis_title="Constante cinética (k)",
                        template="plotly_white"
                    )

                    st.plotly_chart(
                        fig_k,
                        use_container_width=True
                    )

                    # ----------------------------------------
                    # 10. CONCLUSIONES AUTOMÁTICAS
                    # ----------------------------------------

                    st.subheader(
                        "Conclusiones automáticas del análisis"
                    )

                    primera = tabla_pred.iloc[0]
                    ultima = tabla_pred.iloc[-1]

                    if len(tabla_pred) >= 2:

                        if (
                            ultima["Temperatura (K)"]
                            > primera["Temperatura (K)"]
                        ):

                            if (
                                ultima["k estimada"]
                                > primera["k estimada"]
                            ):

                                st.info(
                                    "Al aumentar la temperatura, "
                                    "se incrementa la constante "
                                    "cinética estimada. Esto indica "
                                    "una mayor velocidad de degradación "
                                    "del producto."
                                )

                            else:

                                st.info(
                                    "Al aumentar la temperatura, "
                                    "la constante cinética estimada "
                                    "disminuye. Se observa un "
                                    "comportamiento inverso."
                                )

                    if Ea_pred > 0:

                        st.write(
                            f"• La energía de activación es positiva "
                            f"({Ea_pred / 1000:.4f} kJ/mol), lo que "
                            "indica que la constante cinética aumenta "
                            "con la temperatura según el modelo."
                        )

                    else:

                        st.warning(
                            "La energía de activación calculada "
                            "es negativa. Se recomienda revisar "
                            "los datos experimentales y el ajuste "
                            "de Arrhenius."
                        )

                    st.write(
                        f"• La constante cinética estimada varía "
                        f"entre {tabla_pred['k estimada'].min():.4e} "
                        f"y {tabla_pred['k estimada'].max():.4e}."
                    )

                    if len(tabla_pred) >= 2:

                        if ultima["t50"] < primera["t50"]:

                            st.write(
                                "• El tiempo t50 disminuye al aumentar "
                                "la temperatura, indicando una menor "
                                "estabilidad del producto."
                            )

                        elif ultima["t50"] > primera["t50"]:

                            st.write(
                                "• El tiempo t50 aumenta al aumentar "
                                "la temperatura."
                            )

                    st.write(
                        "• Los tiempos t50, t98, t95 y t90 permiten "
                        "comparar la estabilidad del producto "
                        "en diferentes condiciones térmicas."
                    )

                    st.caption(
                        "Estas conclusiones son generadas "
                        "automáticamente mediante reglas basadas "
                        "en los resultados matemáticos del modelo. "
                        "No representan una consulta a un modelo "
                        "de inteligencia artificial externo."
                    )

                    # ----------------------------------------
                    # 11. EXPORTAR PREDICCIONES
                    # ----------------------------------------

                    st.subheader(
                        "Descargar predicciones"
                    )

                    csv_pred = tabla_pred.to_csv(
                        index=False
                    ).encode("utf-8-sig")

                    st.download_button(
                        label="Descargar predicciones (CSV)",
                        data=csv_pred,
                        file_name="predicciones_estabilidad.csv",
                        mime="text/csv",
                        key="descargar_predicciones"
                    )            
# ==================================================
# INFORMACION FINAL
# ==================================================

st.divider()

with st.expander("Ecuaciones utilizadas"):

    st.markdown("""
    **Orden cero**

    C = C0 - k0·t

    **Orden uno**

    ln(C) = ln(C0) - k1·t

    **Orden dos**

    1/C = 1/C0 + k2·t

    La selección del modelo se realiza comparando
    los coeficientes de determinación R2.
    """)

st.caption(
    "Análisis cinético mediante el método integral. "
    "Las conversiones de concentración corresponden "
    "a unidades de masa por volumen."
)
