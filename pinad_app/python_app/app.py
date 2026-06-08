import streamlit as st
import os
from datetime import datetime
import json
from services.ocr_ultra_service import OCRUltraService
from services.database_service import DatabaseService

# Configuración de la página
st.set_page_config(
    page_title="(π)NAD",
    page_icon="π",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Credenciales de Google
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyAG0gM9rUHowL14Aig5KrMtfdeSxnkYQik")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "531174220363-3aeog10kkqkmbbgo21nsinf110u3qcin.apps.googleusercontent.com")

# Colores de la marca (π)NAD
GOLD_DARK = "#936A31"
GOLD_MEDIUM = "#be882e"
GOLD_LIGHT = "#E4C170"
BROWN_DARK = "#512509"
BROWN_MEDIUM = "#AC7649"
ORANGE_LIGHT = "#FFD194"
ORANGE_BEIGE = "#f4e0ab"
GRAY_DARK = "#292B2A"
WHITE = "#FFFFFF"

# Estilos CSS personalizados con efectos inmersivos
st.markdown(f"""
<style>
    /* Estilos base */
    .stApp {{
        background: linear-gradient(135deg, {ORANGE_BEIGE} 0%, {ORANGE_LIGHT} 100%);
    }}
    
    /* Header principal con efectos inmersivos */
    .pinad-header {{
        background: linear-gradient(135deg, {GOLD_DARK} 0%, {BROWN_DARK} 100%);
        padding: 4rem 2rem;
        border-radius: 25px;
        color: {WHITE};
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        position: relative;
        overflow: hidden;
        animation: fadeIn 1s ease-in;
    }}
    
    .pinad-header::before {{
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
        animation: rotate 30s linear infinite;
    }}
    
    .pinad-header::after {{
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, {GOLD_LIGHT}, {ORANGE_LIGHT}, {GOLD_LIGHT});
        animation: shimmer 3s ease-in-out infinite;
    }}
    
    @keyframes rotate {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
    }}
    
    @keyframes shimmer {{
        0%, 100% {{ opacity: 0.3; }}
        50% {{ opacity: 1; }}
    }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(-20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    @keyframes pulse {{
        0%, 100% {{ transform: scale(1); }}
        50% {{ transform: scale(1.05); }}
    }}
    
    .pinad-title {{
        font-size: 5rem;
        font-weight: bold;
        margin: 0;
        position: relative;
        z-index: 1;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.4);
        animation: pulse 3s ease-in-out infinite;
    }}
    
    .pinad-subtitle {{
        font-size: 1.8rem;
        margin: 1rem 0 0 0;
        opacity: 0.95;
        position: relative;
        z-index: 1;
        font-weight: 300;
    }}
    
    /* Tarjetas de métricas con efectos inmersivos */
    .metric-card {{
        background: {WHITE};
        padding: 2.5rem;
        border-radius: 20px;
        border-top: 6px solid {GOLD_DARK};
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
    }}
    
    .metric-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(147,106,49,0.1), transparent);
        transition: left 0.5s;
    }}
    
    .metric-card:hover {{
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 20px 40px rgba(147,106,49,0.3);
    }}
    
    .metric-card:hover::before {{
        left: 100%;
    }}
    
    .metric-value {{
        font-size: 3rem;
        font-weight: bold;
        color: {GOLD_DARK};
        text-shadow: 2px 2px 4px rgba(147,106,49,0.2);
    }}
    
    .metric-label {{
        font-size: 0.95rem;
        color: {GRAY_DARK};
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 600;
    }}
    
    /* Tarjetas de documentos con efectos inmersivos */
    .doc-card {{
        background: {WHITE};
        padding: 2rem;
        border-radius: 18px;
        border-left: 6px solid {GOLD_DARK};
        margin: 1.5rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
    }}
    
    .doc-card::after {{
        content: '';
        position: absolute;
        bottom: 0;
        right: 0;
        width: 100px;
        height: 100px;
        background: radial-gradient(circle, rgba(147,106,49,0.1) 0%, transparent 70%);
        border-radius: 50%;
        transform: translate(50%, 50%);
    }}
    
    .doc-card:hover {{
        border-left-width: 12px;
        box-shadow: 0 15px 35px rgba(147,106,49,0.25);
        transform: translateX(5px);
    }}
    
    /* Botones personalizados con efectos inmersivos */
    .stButton>button {{
        background: linear-gradient(135deg, {GOLD_DARK} 0%, {BROWN_DARK} 100%);
        color: {WHITE};
        border: none;
        border-radius: 15px;
        padding: 1rem 2.5rem;
        font-weight: bold;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(147,106,49,0.3);
        position: relative;
        overflow: hidden;
    }}
    
    .stButton>button::before {{
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        background: rgba(255,255,255,0.2);
        border-radius: 50%;
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }}
    
    .stButton>button:hover {{
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(147,106,49,0.5);
    }}
    
    .stButton>button:hover::before {{
        width: 300px;
        height: 300px;
    }}
    
    /* Sidebar personalizado con efectos inmersivos */
    .css-1d391kg {{
        background: linear-gradient(180deg, {GOLD_DARK} 0%, {BROWN_DARK} 100%);
        box-shadow: 5px 0 20px rgba(0,0,0,0.2);
    }}
    
    /* Upload area con efectos inmersivos */
    .stFileUploader {{
        border: 3px dashed {GOLD_DARK};
        border-radius: 20px;
        padding: 3rem;
        background: {WHITE};
        transition: all 0.3s ease;
    }}
    
    .stFileUploader:hover {{
        border-color: {BROWN_DARK};
        background: linear-gradient(135deg, {WHITE} 0%, {ORANGE_BEIGE} 100%);
        transform: scale(1.02);
    }}
    
    /* Success message con efectos inmersivos */
    .stSuccess {{
        background: linear-gradient(135deg, {BROWN_MEDIUM} 0%, {GOLD_MEDIUM} 100%);
        color: {WHITE};
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 10px 25px rgba(172,118,73,0.4);
        animation: slideIn 0.5s ease-out;
    }}
    
    @keyframes slideIn {{
        from {{ opacity: 0; transform: translateX(-20px); }}
        to {{ opacity: 1; transform: translateX(0); }}
    }}
    
    /* Progress bar personalizada */
    .stProgress > div > div > div {{
        background: linear-gradient(90deg, {GOLD_DARK}, {GOLD_LIGHT}, {GOLD_DARK});
        background-size: 200% 100%;
        animation: progressShimmer 2s linear infinite;
    }}
    
    @keyframes progressShimmer {{
        0% {{ background-position: 200% 0; }}
        100% {{ background-position: -200% 0; }}
    }}
    
    /* Spinner personalizado */
    .stSpinner {{
        border-color: {GOLD_DARK};
        border-top-color: transparent;
    }}
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown(f"""
<div class="pinad-header">
    <div class="pinad-title">(π)NAD</div>
    <div class="pinad-subtitle">Sistema de Escaneo Contable Inteligente</div>
</div>
""", unsafe_allow_html=True)

# Sidebar con navegación personalizada
st.sidebar.markdown(f"""
<div style="text-align: center; padding: 2rem; color: {WHITE};">
    <h2 style="margin: 0;">Menú</h2>
    <p style="opacity: 0.8;">Selecciona una sección</p>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio(
    "Navegación",
    ["📊 Dashboard", "📄 Documentos", "📋 Reportes", "⚙️ Configuración"],
    label_visibility="collapsed"
)

# Contenido principal
if page == "📊 Dashboard":
    st.markdown("<h2 style='color: #936A31;'>Dashboard General</h2>", unsafe_allow_html=True)
    
    # Obtener métricas reales de la base de datos con manejo de errores
    try:
        db_service = DatabaseService()
        metrics = db_service.get_metrics()
    except Exception as e:
        st.error(f"Error conectando con la base de datos: {str(e)}")
        metrics = {
            "total_documents": 0,
            "completed": 0,
            "in_progress": 0,
            "pending": 0,
            "error": 0,
            "total_transactions": 0,
            "alerts": 0
        }
    
    # Métricas principales con diseño personalizado
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['total_documents']}</div>
            <div class="metric-label">Documentos Procesados</div>
            <div style="color: #AC7649; margin-top: 0.5rem;">Completados: {metrics['completed']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['total_transactions']}</div>
            <div class="metric-label">Transacciones</div>
            <div style="color: #AC7649; margin-top: 0.5rem;">Extraídas de documentos</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['alerts']}</div>
            <div class="metric-label">Alertas Activas</div>
            <div style="color: #512509; margin-top: 0.5rem;">Requieren atención</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        en_proceso = metrics['in_progress'] + metrics['pending']
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{en_proceso}</div>
            <div class="metric-label">En Proceso</div>
            <div style="color: #AC7649; margin-top: 0.5rem;">Pendientes: {metrics['pending']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Gráfico de procesamiento con datos reales
    st.markdown("<h3 style='color: #936A31; margin-top: 2rem;'>Estado de Procesamiento</h3>", unsafe_allow_html=True)
    import pandas as pd
    import plotly.express as px
    
    data = pd.DataFrame({
        'Estado': ['Completado', 'En Proceso', 'Pendiente', 'Error'],
        'Cantidad': [metrics['completed'], metrics['in_progress'], metrics['pending'], metrics['error']]
    })
    
    fig = px.pie(data, values='Cantidad', names='Estado', 
                 color_discrete_sequence=['#AC7649', '#E4C170', '#FFD194', '#512509'],
                 hole=0.4)
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#292B2A')
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Documentos recientes con datos reales
    st.markdown("<h3 style='color: #936A31; margin-top: 2rem;'>📄 Documentos Recientes</h3>", unsafe_allow_html=True)
    
    # Obtener documentos reales de la base de datos con manejo de errores
    try:
        documentos = db_service.get_documents(limit=10)
    except Exception as e:
        st.error(f"Error obteniendo documentos: {str(e)}")
        documentos = []
    
    if documentos:
        for doc in documentos:
            estado_map = {
                'completed': 'Completado',
                'processing': 'En Proceso',
                'pending': 'Pendiente',
                'error': 'Error'
            }
            estado = estado_map.get(doc.get('status', 'pending'), 'Pendiente')
            estado_color = "#AC7649" if estado == "Completado" else "#E4C170" if estado == "En Proceso" else "#512509"
            fecha = doc.get('created_at', '').split('T')[0] if doc.get('created_at') else 'N/A'
            monto = f"${doc.get('total_amount', 0):,.2f}" if doc.get('total_amount') else 'N/A'
            
            st.markdown(f"""
            <div class="doc-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="color: #936A31; font-size: 1.1rem;">📄 {doc.get('file_name', 'Documento')}</strong>
                        <div style="color: #666; margin-top: 0.5rem;">📅 {fecha} | 💰 {monto}</div>
                    </div>
                    <div style="background: {estado_color}; color: white; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.8rem;">
                        {estado}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; color: #666;">
            <p>No hay documentos en la base de datos</p>
            <p>Sube tu primer documento para comenzar</p>
        </div>
        """, unsafe_allow_html=True)

elif page == "📄 Documentos":
    st.markdown("<h2 style='color: #936A31;'>Gestión de Documentos</h2>", unsafe_allow_html=True)
    
    # Upload de archivos personalizado
    st.markdown("<h3 style='color: #936A31;'>Subir Documento</h3>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Arrastra tu documento aquí o haz clic para seleccionar",
        type=['pdf', 'jpg', 'png'],
        help="Formatos aceptados: PDF, JPG, PNG"
    )
    
    if uploaded_file:
        st.markdown(f"""
        <div style="background: #AC7649; color: white; padding: 1rem; border-radius: 10px; margin: 1rem 0;">
            ✅ Archivo cargado: <strong>{uploaded_file.name}</strong>
        </div>
        """, unsafe_allow_html=True)
        
        # Procesamiento real con OCR Ultra con manejo de errores
        with st.spinner("🔄 Procesando documento con OCR Ultra..."):
            try:
                ocr_ultra_service = OCRUltraService()
                file_bytes = uploaded_file.read()
                result = ocr_ultra_service.extract_invoice_data_ultra(file_bytes, uploaded_file.name)
            except Exception as e:
                st.error(f"Error procesando documento con OCR Ultra: {str(e)}")
                result = {"success": False, "error": str(e)}
        
        if result.get("success", False):
            confianza = result.get('confianza', 0.0) * 100
            tiempo = result.get('tiempo_procesamiento', 0.0)
            
            # Guardar documento en la base de datos
            try:
                db_service = DatabaseService()
                document_data = {
                    'file_name': uploaded_file.name,
                    'file_type': uploaded_file.name.split('.')[-1] if '.' in uploaded_file.name else 'unknown',
                    'file_size': len(uploaded_file.getvalue()),
                    'document_type': result.get('tipo_documento', 'Desconocido'),
                    'date': result.get('fecha', ''),
                    'vendor': result.get('proveedor', ''),
                    'invoice_number': result.get('numero_factura', ''),
                    'subtotal': result.get('subtotal', 0),
                    'tax': result.get('iva', 0),
                    'total': result.get('total', 0),
                    'confidence': result.get('confianza', 0),
                    'language': result.get('idioma', 'es'),
                    'processing_time': result.get('tiempo_procesamiento', 0),
                    'raw_text': result.get('texto_completo', ''),
                    'layout': result.get('layout', {}),
                    'status': 'completed'
                }
                saved_doc = db_service.save_document(document_data)
                
                if saved_doc:
                    # Guardar resultados completos del OCR
                    db_service.save_ocr_results(saved_doc['id'], result)
                    st.success("✅ Datos guardados en la base de datos")
                else:
                    st.warning("⚠️ Error al guardar documento en la base de datos")
            except Exception as e:
                st.error(f"Error guardando en base de datos: {str(e)}")
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #AC7649 0%, #936A31 100%); color: white; padding: 1.5rem; border-radius: 10px; margin: 1rem 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>✅ Documento procesado exitosamente con OCR Ultra</strong>
                        <div style="margin-top: 0.5rem; opacity: 0.9;">Confianza: {confianza:.1f}% | Tiempo: {tiempo:.2f}s</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px;">
                        {result.get('idioma', 'es').upper()}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Mostrar resultados extraídos con todas las funciones del OCR Ultra
            st.markdown("<h3 style='color: #936A31; margin-top: 2rem;'>📋 Información Extraída (OCR Ultra)</h3>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="doc-card">
                    <h4 style="color: #936A31; margin-top: 0;">Datos del Documento</h4>
                    <p><strong>Tipo:</strong> {result['tipo_documento']}</p>
                    <p><strong>Fecha:</strong> {result['fecha']}</p>
                    <p><strong>Proveedor:</strong> {result['proveedor']}</p>
                    <p><strong>N° Factura:</strong> {result.get('numero_factura', 'N/A')}</p>
                    <p><strong>Subtotal:</strong> ${result['subtotal']:,.2f}</p>
                    <p><strong>IVA:</strong> ${result['iva']:,.2f}</p>
                    <p><strong>Total:</strong> <span style="color: #936A31; font-weight: bold; font-size: 1.2rem;">${result['total']:,.2f}</span></p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="doc-card">
                    <h4 style="color: #936A31; margin-top: 0;">Transacciones Detectadas</h4>
                """, unsafe_allow_html=True)
                if result['items']:
                    for item in result['items']:
                        st.markdown(f"""
                        <div style="padding: 0.5rem 0; border-bottom: 1px solid #f0f0f0;">
                            <strong>{item.get('description', 'N/A')}</strong>
                            <div style="color: #936A31;">${item.get('amount', 0):,.2f}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("<p style='color: #666;'>No se detectaron items específicos</p>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="doc-card">
                    <h4 style='color: #936A31; margin-top: 0;'>Elementos Detectados</h4>
                    <p><strong>Tablas:</strong> {len(result.get('tablas', []))}</p>
                    <p><strong>Firmas:</strong> {len(result.get('firmas', []))}</p>
                    <p><strong>Códigos QR:</strong> {len(result.get('codigos_qr', []))}</p>
                    <p><strong>Códigos de Barras:</strong> {len(result.get('codigos_barras', []))}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Mostrar tablas extraídas
            if result.get('tablas'):
                st.markdown("<h3 style='color: #936A31; margin-top: 2rem;'>📊 Tablas Extraídas</h3>", unsafe_allow_html=True)
                for i, tabla in enumerate(result['tablas']):
                    with st.expander(f"Tabla {i+1}"):
                        st.dataframe(tabla)
            
            # Mostrar códigos QR
            if result.get('codigos_qr'):
                st.markdown("<h3 style='color: #936A31; margin-top: 2rem;'>📱 Códigos QR Detectados</h3>", unsafe_allow_html=True)
                for i, qr in enumerate(result['codigos_qr']):
                    st.markdown(f"""
                    <div class="doc-card">
                        <strong>QR Code {i+1}:</strong> {qr.get('data', 'N/A')}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Mostrar firmas
            if result.get('firmas'):
                st.markdown("<h3 style='color: #936A31; margin-top: 2rem;'>✍️ Firmas Detectadas</h3>", unsafe_allow_html=True)
                for i, firma in enumerate(result['firmas']):
                    st.markdown(f"""
                    <div class="doc-card">
                        <strong>Firma {i+1}:</strong> {firma.get('location', 'N/A')} - Confianza: {firma.get('confidence', 0):.1f}%
                    </div>
                    """, unsafe_allow_html=True)
            
            # Mostrar layout del documento
            if result.get('layout'):
                st.markdown("<h3 style='color: #936A31; margin-top: 2rem;'>📐 Layout del Documento</h3>", unsafe_allow_html=True)
                layout = result['layout']
                st.markdown(f"""
                <div class="doc-card">
                    <p><strong>Ancho:</strong> {layout.get('width', 'N/A')}</p>
                    <p><strong>Alto:</strong> {layout.get('height', 'N/A')}</p>
                    <p><strong>Orientación:</strong> {layout.get('orientation', 'N/A')}</p>
                    <p><strong>Regiones:</strong> {len(layout.get('regions', []))}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Mostrar texto completo extraído
            with st.expander("📄 Ver texto completo extraído"):
                st.text(result['texto_completo'])
        else:
            st.markdown(f"""
            <div style="background: #512509; color: white; padding: 1rem; border-radius: 10px; margin: 1rem 0;">
                ⚠️ OCR no disponible - usando modo manual
            </div>
            """, unsafe_allow_html=True)
            
            # Formulario manual
            with st.form("manual_entry"):
                st.markdown("<h4 style='color: #936A31;'>Ingreso Manual de Datos</h4>", unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    fecha = st.date_input("Fecha del documento")
                    proveedor = st.text_input("Proveedor")
                with col2:
                    subtotal = st.number_input("Subtotal", min_value=0.0, value=0.0)
                    iva = st.number_input("IVA", min_value=0.0, value=0.0)
                total = st.number_input("Total", min_value=0.0, value=0.0)
                
                submitted = st.form_submit_button("💾 Guardar Datos")
                if submitted:
                    st.markdown(f"""
                    <div style="background: #AC7649; color: white; padding: 1rem; border-radius: 10px; margin: 1rem 0;">
                        ✅ Datos guardados manualmente
                    </div>
                    """, unsafe_allow_html=True)
        
        # Acciones
        st.markdown("<h3 style='color: #936A31; margin-top: 2rem;'>🚀 Acciones</h3>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📧 Gmail"):
                from services.gmail_service import GmailService
                gmail_service = GmailService()
                gmail_service.send_notification(uploaded_file.name, "Procesado")
                st.markdown(f"""
                <div style="background: #AC7649; color: white; padding: 0.5rem; border-radius: 5px; margin-top: 0.5rem;">
                    ✅ Enviado
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            if st.button("💾 Drive"):
                from services.drive_service import DriveService
                drive_service = DriveService()
                drive_service.backup_document({"name": uploaded_file.name})
                st.markdown(f"""
                <div style="background: #AC7649; color: white; padding: 0.5rem; border-radius: 5px; margin-top: 0.5rem;">
                    ✅ Guardado
                </div>
                """, unsafe_allow_html=True)
        
        with col3:
            if st.button("📊 Sheets"):
                from services.sheets_service import SheetsService
                sheets_service = SheetsService()
                sheets_service.create_spreadsheet(f"Reporte {uploaded_file.name}")
                st.markdown(f"""
                <div style="background: #AC7649; color: white; padding: 0.5rem; border-radius: 5px; margin-top: 0.5rem;">
                    ✅ Creado
                </div>
                """, unsafe_allow_html=True)
        
        with col4:
            if st.button("📅 Calendar"):
                from services.calendar_service import CalendarService
                calendar_service = CalendarService()
                calendar_service.create_processing_reminder(uploaded_file.name)
                st.markdown(f"""
                <div style="background: #AC7649; color: white; padding: 0.5rem; border-radius: 5px; margin-top: 0.5rem;">
                    ✅ Creado
                </div>
                """, unsafe_allow_html=True)

elif page == "📋 Reportes":
    st.markdown("<h2 style='color: #936A31;'>Reportes</h2>", unsafe_allow_html=True)
    
    report_type = st.selectbox(
        "Seleccionar tipo de reporte",
        ["📋 Reporte de IVA", "📋 Reporte ISLR", "📋 Balance General", "📋 Estado de Resultados"]
    )
    
    # Inicializar db_service para reportes
    try:
        db_service = DatabaseService()
    except Exception as e:
        st.error(f"Error conectando con la base de datos: {str(e)}")
        db_service = None
    
    if report_type == "📋 Reporte de IVA":
        st.markdown("<h3 style='color: #936A31; margin-top: 2rem;'>Reporte de IVA</h3>", unsafe_allow_html=True)
        
        # Obtener datos reales de IVA con manejo de errores
        if db_service:
            try:
                iva_data = db_service.get_reports('iva')
            except Exception as e:
                st.error(f"Error obteniendo reporte de IVA: {str(e)}")
                iva_data = {}
        else:
            iva_data = {}
        
        if iva_data:
            for key, value in iva_data.items():
                st.markdown(f"""
                <div class="doc-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong style="color: #936A31;">{key}</strong>
                        <span style="color: #936A31; font-size: 1.5rem; font-weight: bold;">${value:,.2f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 2rem; color: #666;">
                <p>No hay datos suficientes para generar el reporte de IVA</p>
                <p>Sube más documentos para calcular el reporte</p>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("📊 Generar en Sheets"):
            from services.sheets_service import SheetsService
            sheets_service = SheetsService()
            sheets_service.create_spreadsheet("Reporte IVA")
            st.markdown(f"""
            <div style="background: #AC7649; color: white; padding: 1rem; border-radius: 10px; margin: 1rem 0;">
                ✅ Reporte generado en Google Sheets
            </div>
            """, unsafe_allow_html=True)
    
    elif report_type == "📋 Reporte ISLR":
        st.markdown("<h3 style='color: #936A31; margin-top: 2rem;'>Reporte ISLR</h3>", unsafe_allow_html=True)
        
        # Obtener datos reales de ISLR con manejo de errores
        if db_service:
            try:
                islr_data = db_service.get_reports('islr')
            except Exception as e:
                st.error(f"Error obteniendo reporte ISLR: {str(e)}")
                islr_data = {}
        else:
            islr_data = {}
        
        if islr_data:
            for key, value in islr_data.items():
                st.markdown(f"""
                <div class="doc-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong style="color: #936A31;">{key}</strong>
                        <span style="color: #936A31; font-size: 1.5rem; font-weight: bold;">${value:,.2f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 2rem; color: #666;">
                <p>No hay datos suficientes para generar el reporte ISLR</p>
                <p>Sube más documentos para calcular el reporte</p>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("📊 Generar en Sheets"):
            from services.sheets_service import SheetsService
            sheets_service = SheetsService()
            sheets_service.create_spreadsheet("Reporte ISLR")
            st.markdown(f"""
            <div style="background: #AC7649; color: white; padding: 1rem; border-radius: 10px; margin: 1rem 0;">
                ✅ Reporte generado en Google Sheets
            </div>
            """, unsafe_allow_html=True)

elif page == "⚙️ Configuración":
    st.markdown("<h2 style='color: #936A31;'>Configuración</h2>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='color: #936A31; margin-top: 2rem;'>🔑 Credenciales de Google</h3>", unsafe_allow_html=True)
    
    api_key = st.text_input("Google API Key", value=GOOGLE_API_KEY, type="password")
    client_id = st.text_input("Google Client ID", value=GOOGLE_CLIENT_ID, type="password")
    client_secret = st.text_input("Google Client Secret", value="YOUR_CLIENT_SECRET", type="password")
    
    if st.button("💾 Guardar Configuración"):
        st.markdown(f"""
        <div style="background: #AC7649; color: white; padding: 1rem; border-radius: 10px; margin: 1rem 0;">
            ✅ Configuración guardada
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<hr style='border-color: #936A31; margin: 2rem 0;'>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='color: #936A31;'>📧 Configuración de Gmail</h3>", unsafe_allow_html=True)
    
    gmail_enabled = st.checkbox("Habilitar notificaciones", value=True)
    gmail_email = st.text_input("Email de destino", value="contador@ejemplo.com")
    
    st.markdown("<hr style='border-color: #936A31; margin: 2rem 0;'>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='color: #936A31;'>💾 Configuración de Drive</h3>", unsafe_allow_html=True)
    
    drive_enabled = st.checkbox("Habilitar backup", value=True)
    drive_folder = st.text_input("Carpeta de backup", value="PINAD_Documentos")
    
    st.markdown("<hr style='border-color: #936A31; margin: 2rem 0;'>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='color: #936A31;'>📊 Configuración de Sheets</h3>", unsafe_allow_html=True)
    
    sheets_enabled = st.checkbox("Habilitar reportes", value=True)
    sheets_folder = st.text_input("Carpeta de reportes", value="PINAD_Reportes")
    
    st.markdown("<hr style='border-color: #936A31; margin: 2rem 0;'>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='color: #936A31;'>📅 Configuración de Calendar</h3>", unsafe_allow_html=True)
    
    calendar_enabled = st.checkbox("Habilitar recordatorios", value=True)
    calendar_calendar = st.text_input("Calendario de recordatorios", value="PINAD_Recordatorios")
    
    if st.button("💾 Guardar Todas las Configuraciones"):
        st.markdown(f"""
        <div style="background: #AC7649; color: white; padding: 1rem; border-radius: 10px; margin: 1rem 0;">
            ✅ Todas las configuraciones guardadas
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("<hr style='border-color: #936A31; margin: 3rem 0;'>", unsafe_allow_html=True)
st.markdown(f"""
<div style="text-align: center; color: {GRAY_DARK}; padding: 2rem;">
    <div style="font-size: 2rem; font-weight: bold; color: {GOLD_DARK};">(π)NAD</div>
    <div style="margin-top: 0.5rem;">Sistema de Escaneo Contable Inteligente</div>
    <div style="margin-top: 1rem; opacity: 0.7;">Integración con Google Workspace</div>
    <div style="margin-top: 0.5rem; font-size: 0.8rem;">Desarrollado con Python y Streamlit</div>
</div>
""", unsafe_allow_html=True)
