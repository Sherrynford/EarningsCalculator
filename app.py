import streamlit as st
import pandas as pd
from io import BytesIO

# ==================================================
# CONFIGURACIÓN
# ==================================================
st.set_page_config(page_title="Profitability Calculator", layout="centered")

# ==================================================
# LOGIN SIMPLE CON st.secrets (SEGURO LOCAL + CLOUD)
# ==================================================
try:
    APP_PASSWORD = st.secrets["APP_PASSWORD"]
except Exception:
    APP_PASSWORD = "1234"  # fallback local

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Access")
    password = st.text_input("Password", type="password")
    if st.button("Enter"):
        if password == APP_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect Password")
    st.stop()

# ==================================================
# IDIOMA
# ==================================================
language = st.sidebar.selectbox(
    "🌐 Language / Idioma",
    ("English", "Español")
)

# ==================================================
# SIDEBAR – NIVELES DE RENTABILIDAD
# ==================================================
st.sidebar.markdown("---")

if language == "Español":
    st.sidebar.markdown("""
### 📈 Niveles de rentabilidad
< 0% 🔴 **Pérdida**  
0 – 5% ⚠️ **Muy bajo (riesgo alto)**  
5 – 10% 🟡 **Rentable pero frágil**  
10 – 20% 🟢 **Saludable**  
+20% 🚀 **Muy rentable**
""")
else:
    st.sidebar.markdown("""
### 📈 Profitability levels
< 0% 🔴 **Loss**  
0 – 5% ⚠️ **Very low (high risk)**  
5 – 10% 🟡 **Profitable but fragile**  
10 – 20% 🟢 **Healthy**  
+20% 🚀 **Very profitable**
""")

# ==================================================
# TEXTOS
# ==================================================
TEXT = {
    "Español": {
        "title": "📊 Calculadora de Rentabilidad",
        "subtitle": "Calcula ganancias reales considerando todos tus gastos",
        "products": "1️⃣ Productos / Servicios",
        "add_product": "➕ Agregar",
        "remove_product": "🗑 Eliminar",
        "name": "Nombre Producto/Servicio",
        "price": "Precio de venta",
        "units": "Unidades vendidas al mes",
        "cv": "Costos variables por unidad",
        "materia": "Materia prima",
        "envio": "Envío",
        "comision": "Comisiones",
        "cf": "2️⃣ Costos fijos mensuales",
        "arriendo": "Arriendo",
        "internet": "Internet",
        "publicidad": "Publicidad",
        "otros": "Otros gastos",
        "results": "3️⃣ Resultados",
        "revenue": "Ingresos totales",
        "expenses": "Gastos totales",
        "profit": "Ganancia / Pérdida",
        "margin": "Margen (%)",
        "rentable": "🟢 Tu negocio ES rentable",
        "no_rentable": "🔴 Tu negocio NO es rentable",
        "download": "📥 Descargar Excel",
        "disclaimer": "Herramienta orientativa. No reemplaza asesoría financiera."
    },
    "English": {
        "title": "📊 Profitability Calculator",
        "subtitle": "Calculate real profits including all expenses",
        "products": "1️⃣ Products / Services",
        "add_product": "➕ Add",
        "remove_product": "🗑 Remove",
        "name": "Name Product/Service",
        "price": "Selling price",
        "units": "Units sold per month",
        "cv": "Variable costs per unit",
        "materia": "Raw materials",
        "envio": "Shipping",
        "comision": "Fees",
        "cf": "2️⃣ Monthly fixed costs",
        "arriendo": "Rent",
        "internet": "Internet",
        "publicidad": "Advertising",
        "otros": "Other expenses",
        "results": "3️⃣ Results",
        "revenue": "Total revenue",
        "expenses": "Total expenses",
        "profit": "Profit / Loss",
        "margin": "Margin (%)",
        "rentable": "🟢 Your business IS profitable",
        "no_rentable": "🔴 Your business is NOT profitable",
        "download": "📥 Download Excel",
        "disclaimer": "Indicative tool. Does not replace financial advice."
    }
}

t = TEXT[language]

# ==================================================
# FORMATO DE DINERO
# ==================================================
def format_money(value):
    value = int(round(value, 0))
    if language == "Español":
        return "$" + f"{value:,}".replace(",", ".")
    else:
        return "$" + f"{value:,}"

# ==================================================
# SESSION STATE
# ==================================================
if "products" not in st.session_state:
    st.session_state.products = [{
        "name": "",
        "price": 0.0,
        "units": 0,
        "cv_materia": 0.0,
        "cv_envio": 0.0,
        "cv_comision": 0.0
    }]

# ==================================================
# UI
# ==================================================
st.title(t["title"])
st.caption(t["subtitle"])

# ==================================================
# PRODUCTOS (INTERFAZ MINIMALISTA)
# ==================================================
st.header(t["products"])

delete_index = None
total_revenue = 0
total_units = 0
total_variable_costs = 0

for i, p in enumerate(st.session_state.products):

    # Columnas para nombre, precio y unidades
    col1, col2, col3 = st.columns([2, 2, 2])
    p["name"] = col1.text_input(t["name"], value=p["name"], key=f"name_{i}")
    
    # Dejar vacío si es 0
    p["price"] = col2.number_input(
        t["price"], 
        min_value=0.0, 
        step=50.0, 
        value=p["price"] if p["price"] > 0 else 0.0, 
        format="%.2f", 
        key=f"price_{i}"
    )
    p["units"] = col3.number_input(
        t["units"], 
        min_value=0, 
        step=1, 
        value=p["units"] if p["units"] > 0 else 0, 
        key=f"units_{i}"
    )

    # Columnas para costos variables
    st.text(t["cv"])
    col4, col5, col6 = st.columns([2, 2, 2])
    p["cv_materia"] = col4.number_input(
        t["materia"], 
        min_value=0.0, 
        step=50.0, 
        value=p["cv_materia"] if p["cv_materia"] > 0 else 0.0, 
        format="%.2f", 
        key=f"mat_{i}"
    )
    p["cv_envio"] = col5.number_input(
        t["envio"], 
        min_value=0.0, 
        step=50.0, 
        value=p["cv_envio"] if p["cv_envio"] > 0 else 0.0, 
        format="%.2f", 
        key=f"env_{i}"
    )
    p["cv_comision"] = col6.number_input(
        t["comision"], 
        min_value=0.0, 
        step=50.0, 
        value=p["cv_comision"] if p["cv_comision"] > 0 else 0.0, 
        format="%.2f", 
        key=f"com_{i}"
    )

    # Botón eliminar
    if st.button(t["remove_product"], key=f"del_{i}"):
        delete_index = i

    # Acumuladores
    total_revenue += p["price"] * p["units"]
    total_units += p["units"]
    total_variable_costs += (p["cv_materia"] + p["cv_envio"] + p["cv_comision"]) * p["units"]

# Eliminar producto si corresponde
if delete_index is not None and len(st.session_state.products) > 1:
    st.session_state.products.pop(delete_index)
    st.rerun()

# Botón agregar producto
if st.button(t["add_product"]):
    st.session_state.products.append({
        "name": "",
        "price": 0.0,
        "units": 0,
        "cv_materia": 0.0,
        "cv_envio": 0.0,
        "cv_comision": 0.0
    })
    st.rerun()

# ==================================================
# COSTOS FIJOS (MINIMALISTA)
# ==================================================
st.header(t["cf"])

col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
arriendo = col1.number_input(t["arriendo"], min_value=0.0, step=1000.0, value=0.0)
internet = col2.number_input(t["internet"], min_value=0.0, step=1000.0, value=0.0)
publicidad = col3.number_input(t["publicidad"], min_value=0.0, step=1000.0, value=0.0)
otros = col4.number_input(t["otros"], min_value=0.0, step=1000.0, value=0.0)

costos_fijos = arriendo + internet + publicidad + otros

# ==================================================
# RESULTADOS
# ==================================================
st.header(t["results"])

gastos_totales = total_variable_costs + costos_fijos
ganancia = total_revenue - gastos_totales
margen = (ganancia / total_revenue * 100) if total_revenue > 0 else 0

st.metric(t["revenue"], format_money(total_revenue))
st.metric(t["expenses"], format_money(gastos_totales))
st.metric(t["profit"], format_money(ganancia))
st.metric(t["margin"], f"{margen:.1f}%")

if ganancia > 0:
    st.success(t["rentable"])
else:
    st.error(t["no_rentable"])

# ==================================================
# EXPORTAR A EXCEL (ES + EN)
# ==================================================
rows_es = []
rows_en = []

for p in st.session_state.products:
    rows_es.append({
        "Producto / Servicio": p["name"],
        "Precio": p["price"],
        "Unidades": p["units"],
        "Ingresos": p["price"] * p["units"],
        "Costo variable unitario": p["cv_materia"] + p["cv_envio"] + p["cv_comision"]
    })

    rows_en.append({
        "Product / Service": p["name"],
        "Price": p["price"],
        "Units": p["units"],
        "Revenue": p["price"] * p["units"],
        "Variable cost per unit": p["cv_materia"] + p["cv_envio"] + p["cv_comision"]
    })

df_es = pd.DataFrame(rows_es)
df_en = pd.DataFrame(rows_en)

resumen_es = pd.DataFrame({
    "Concepto": ["Ingresos", "Costos variables", "Costos fijos", "Ganancia", "Margen %"],
    "Monto": [total_revenue, total_variable_costs, costos_fijos, ganancia, margen]
})

resumen_en = pd.DataFrame({
    "Concept": ["Revenue", "Variable costs", "Fixed costs", "Profit", "Margin %"],
    "Amount": [total_revenue, total_variable_costs, costos_fijos, ganancia, margen]
})

output = BytesIO()
with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
    df_es.to_excel(writer, index=False, sheet_name="Productos_ES")
    resumen_es.to_excel(writer, index=False, sheet_name="Resumen_ES")

    df_en.to_excel(writer, index=False, sheet_name="Products_EN")
    resumen_en.to_excel(writer, index=False, sheet_name="Summary_EN")

st.download_button(
    label=t["download"],
    data=output.getvalue(),
    file_name="profitability.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.caption(t["disclaimer"])
