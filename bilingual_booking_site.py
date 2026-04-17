import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Bilingual Booking & Conversion System",
    page_icon="📅",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main {
        background: linear-gradient(180deg, #f8fbff 0%, #eef4ff 100%);
    }
    .hero-box {
        background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 100%);
        color: white;
        padding: 2rem;
        border-radius: 22px;
        margin-bottom: 1rem;
        box-shadow: 0 14px 30px rgba(15, 23, 42, 0.18);
    }
    .hero-box h1 {
        margin: 0 0 .5rem 0;
        font-size: 2.3rem;
    }
    .hero-box p {
        margin: 0;
        font-size: 1.05rem;
        opacity: .96;
    }
    .info-card {
    background: #ffffff;
    padding: 1.25rem 1.5rem;
    border-radius: 16px;
    border: 1px solid rgba(148, 163, 184, 0.2);
    box-shadow: 0 6px 20px rgba(15, 23, 42, 0.08);
    margin-bottom: 1rem;
    color: #111827; /* FIX: dark readable text */
    transition: all 0.2s ease;
}

/* Text inside card */
.info-card h1,
.info-card h2,
.info-card h3,
.info-card h4 {
    color: #0f172a;
    font-weight: 600;
    margin-bottom: 0.4rem;
}

.info-card p,
.info-card span,
.info-card div {
    color: #374151;
    font-size: 0.95rem;
}

/* Hover effect (makes it feel premium) */
.info-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.12);
}
.stRadio > div {
    background: rgba(255,255,255,0.05);
    padding: 6px 10px;
    border-radius: 10px;
}
.info-card,
.soft-panel {
    padding: 1.5rem 1.75rem;
}
.service-card {
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.service-card {
    transition: all 0.2s ease;
}

.service-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 30px rgba(0,0,0,0.15);
}
.service-card {
    border: 1px solid rgba(255,255,255,0.08);
}
.section-title {
    font-size: 1.8rem;
    font-weight: 800;
    letter-spacing: -0.5px;
}
.section-title {
    font-size: 1.6rem;
    font-weight: 800;
}
    .section-title {
        font-size: 1.35rem;
        font-weight: 700;
        margin-top: .75rem;
        margin-bottom: .6rem;
        color: #e5e7eb;   /* FIX */
    }
    .soft-panel {
        background: rgba(255,255,255,0.94);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 18px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.05);
    }
    .soft-panel,
.soft-panel h1,
.soft-panel h2,
.soft-panel h3,
.soft-panel h4,
.soft-panel p,
.soft-panel span,
.soft-panel div,
.soft-panel label {
    color: #111827 !important;
}
.soft-panel {
    border-left: 4px solid #3b82f6;
}
.soft-panel,
.info-card {
    transition: all 0.2s ease;
}
    .pill {
        display: inline-block;
        padding: .35rem .7rem;
        border-radius: 999px;
        background: #dbeafe;
        color: #1d4ed8;
        font-size: .9rem;
        margin-right: .4rem;
        margin-bottom: .4rem;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

DB_PATH = Path("booking_system.db")

TRANSLATIONS = {
    "English": {
        "app_title": "Bilingual Service Booking & Lead Conversion System",
        "hero_title": "Book a service in minutes",
        "hero_subtitle": "English/Spanish lead capture, qualification, booking, and saved interaction history.",
        "language": "Language",
        "nav_home": "Home",
        "nav_customer": "Customer Form",
        "nav_admin": "Admin Dashboard",
        "service_needed": "What service do you need?",
        "name": "Full name",
        "phone": "Phone number",
        "email": "Email address",
        "address": "Service address",
        "details": "Describe what you need",
        "urgency": "How urgent is this?",
        "urgency_low": "Low - flexible",
        "urgency_medium": "Medium - this week",
        "urgency_high": "High - urgent",
        "preferred_date": "Preferred date",
        "preferred_time": "Preferred time",
        "submit": "Book appointment",
        "success": "Appointment request saved successfully.",
        "customer_info": "Customer Information",
        "appointment_info": "Appointment Preferences",
        "history_info": "Interaction History Preview",
        "service_options": [
            "House Cleaning",
            "Handyman",
            "Auto Detailing",
            "HVAC",
            "Mobile Notary",
            "Beauty Appointment",
        ],
        "history_1": "Language selected",
        "history_2": "Service selected",
        "history_3": "Urgency selected",
        "history_4": "Appointment requested",
        "admin_title": "Admin Dashboard",
        "admin_subtitle": "View saved leads, booking requests, and interaction history.",
        "refresh": "Refresh data",
        "lead_table": "Saved Leads",
        "history_table": "Interaction History",
        "empty": "No leads yet.",
        "structured_output": "Structured Lead Output",
        "click_phone": "Call",
        "click_email": "Email",
        "click_address": "Open address",
        "booking_cta": "Ready to schedule? Fill out the form below.",
        "hero_badge_1": "Fast booking",
        "hero_badge_2": "Bilingual support",
        "hero_badge_3": "Saved lead history",
        "trust_title": "Why customers choose us",
        "trust_1_title": "Easy booking",
        "trust_1_text": "A guided intake form helps customers choose services, describe the job, and request an appointment quickly.",
        "trust_2_title": "Bilingual experience",
        "trust_2_text": "Customers can complete the flow in English or Spanish with the same functionality.",
        "trust_3_title": "Organized lead tracking",
        "trust_3_text": "Every inquiry is stored with structured contact details and interaction history.",
        "services_title": "Popular services",
        "booking_section_title": "Request your appointment",
        "summary_title": "Booking summary",
        "confirm_title": "Confirmation details",
    },
    "Español": {
        "app_title": "Sistema Bilingüe de Reservas y Conversión de Clientes",
        "hero_title": "Reserva un servicio en minutos",
        "hero_subtitle": "Captura de clientes en inglés/español, calificación, reserva e historial guardado.",
        "language": "Idioma",
        "nav_home": "Inicio",
        "nav_customer": "Formulario del Cliente",
        "nav_admin": "Panel Administrativo",
        "service_needed": "¿Qué servicio necesita?",
        "name": "Nombre completo",
        "phone": "Número de teléfono",
        "email": "Correo electrónico",
        "address": "Dirección del servicio",
        "details": "Describa lo que necesita",
        "urgency": "¿Qué tan urgente es esto?",
        "urgency_low": "Baja - flexible",
        "urgency_medium": "Media - esta semana",
        "urgency_high": "Alta - urgente",
        "preferred_date": "Fecha preferida",
        "preferred_time": "Hora preferida",
        "submit": "Reservar cita",
        "success": "La solicitud de cita se guardó correctamente.",
        "customer_info": "Información del Cliente",
        "appointment_info": "Preferencias de la Cita",
        "history_info": "Vista Previa del Historial de Interacción",
        "service_options": [
            "Limpieza del Hogar",
            "Manitas",
            "Detallado de Autos",
            "HVAC",
            "Notario Móvil",
            "Cita de Belleza",
        ],
        "history_1": "Idioma seleccionado",
        "history_2": "Servicio seleccionado",
        "history_3": "Urgencia seleccionada",
        "history_4": "Cita solicitada",
        "admin_title": "Panel Administrativo",
        "admin_subtitle": "Ver clientes guardados, solicitudes de citas e historial de interacción.",
        "refresh": "Actualizar datos",
        "lead_table": "Clientes Guardados",
        "history_table": "Historial de Interacción",
        "empty": "Aún no hay clientes.",
        "structured_output": "Salida Estructurada del Cliente",
        "click_phone": "Llamar",
        "click_email": "Correo",
        "click_address": "Abrir dirección",
        "booking_cta": "¿Listo para programar? Complete el formulario a continuación.",
        "hero_badge_1": "Reserva rápida",
        "hero_badge_2": "Soporte bilingüe",
        "hero_badge_3": "Historial guardado",
        "trust_title": "Por qué los clientes nos eligen",
        "trust_1_title": "Reserva sencilla",
        "trust_1_text": "Un formulario guiado ayuda a los clientes a elegir servicios, describir el trabajo y solicitar una cita rápidamente.",
        "trust_2_title": "Experiencia bilingüe",
        "trust_2_text": "Los clientes pueden completar el proceso en inglés o español con la misma funcionalidad.",
        "trust_3_title": "Seguimiento organizado",
        "trust_3_text": "Cada consulta se guarda con detalles estructurados e historial de interacción.",
        "services_title": "Servicios populares",
        "booking_section_title": "Solicite su cita",
        "summary_title": "Resumen de la reserva",
        "confirm_title": "Detalles de confirmación",
    },
}


def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


conn = get_connection()


def init_db() -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            language TEXT NOT NULL,
            service TEXT NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            address TEXT,
            details TEXT,
            urgency TEXT,
            preferred_date TEXT,
            preferred_time TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS interaction_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER NOT NULL,
            step_name TEXT NOT NULL,
            response TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (lead_id) REFERENCES leads (id)
        )
        """
    )
    conn.commit()


init_db()


def save_lead(
    language: str,
    service: str,
    name: str,
    phone: str,
    email: str,
    address: str,
    details: str,
    urgency: str,
    preferred_date: str,
    preferred_time: str,
) -> int:
    created_at = datetime.now().isoformat(timespec="seconds")
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO leads (
            created_at, language, service, name, phone, email, address, details, urgency, preferred_date, preferred_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            created_at,
            language,
            service,
            name,
            phone,
            email,
            address,
            details,
            urgency,
            preferred_date,
            preferred_time,
        ),
    )
    lead_id = cursor.lastrowid
    conn.commit()
    return lead_id


def save_history(lead_id: int, step_name: str, response: str) -> None:
    conn.execute(
        "INSERT INTO interaction_history (lead_id, step_name, response, created_at) VALUES (?, ?, ?, ?)",
        (lead_id, step_name, response, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()


def fetch_leads() -> pd.DataFrame:
    return pd.read_sql_query("SELECT * FROM leads ORDER BY id DESC", conn)


def fetch_history() -> pd.DataFrame:
    return pd.read_sql_query(
        """
        SELECT ih.id, ih.lead_id, l.name, l.phone, ih.step_name, ih.response, ih.created_at
        FROM interaction_history ih
        JOIN leads l ON ih.lead_id = l.id
        ORDER BY ih.id DESC
        """,
        conn,
    )


def clean_phone(phone: str) -> str:
    return "".join(ch for ch in phone if ch.isdigit() or ch == "+")


st.session_state.setdefault("language", "English")

header_left, header_right = st.columns([4, 1])
with header_left:
    st.title(TRANSLATIONS[st.session_state["language"]]["app_title"])
with header_right:
    selected_language = st.selectbox(
        TRANSLATIONS[st.session_state["language"]]["language"],
        options=list(TRANSLATIONS.keys()),
        index=list(TRANSLATIONS.keys()).index(st.session_state["language"]),
    )
    st.session_state["language"] = selected_language

T = TRANSLATIONS[st.session_state["language"]]

st.markdown(
    f"""
    <div class="hero-box">
        <h1>{T['hero_title']}</h1>
        <p>{T['hero_subtitle']}</p>
        <div style="margin-top: 1rem;">
            <span class="pill">{T['hero_badge_1']}</span>
            <span class="pill">{T['hero_badge_2']}</span>
            <span class="pill">{T['hero_badge_3']}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

page = st.radio(
    "Navigation",
    [T["nav_home"], T["nav_customer"], T["nav_admin"]],
    horizontal=True,
    label_visibility="collapsed",
)

if page == T["nav_home"]:
    trust_cols = st.columns(3)
    trust_items = [
        (T["trust_1_title"], T["trust_1_text"]),
        (T["trust_2_title"], T["trust_2_text"]),
        (T["trust_3_title"], T["trust_3_text"]),
    ]

    st.markdown(
        f"<div class='section-title'>{T['trust_title']}</div>",
        unsafe_allow_html=True,
    )
    for col, (title, text) in zip(trust_cols, trust_items):
        with col:
            st.markdown(
                f"<div class='info-card'><h4>{title}</h4><p>{text}</p></div>",
                unsafe_allow_html=True,
            )

    st.markdown(
        f"<div class='section-title'>{T['services_title']}</div>",
        unsafe_allow_html=True,
    )
    service_cols = st.columns(3)
    for idx, service_name in enumerate(T["service_options"]):
        with service_cols[idx % 3]:
            st.markdown(
                f"<div class='soft-panel'><strong>{service_name}</strong><br><span style='color:#475569;'>Book this service through the guided intake flow.</span></div>",
                unsafe_allow_html=True,
            )

    st.markdown(
        f"<div class='soft-panel'><strong>{T['booking_cta']}</strong><br>{T['hero_subtitle']}</div>",
        unsafe_allow_html=True,
    )

elif page == T["nav_customer"]:
    left, right = st.columns([1.45, 1])

    with left:
        st.markdown(
            f"<div class='section-title'>{T['booking_section_title']}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='soft-panel'>{T['booking_cta']}</div>",
            unsafe_allow_html=True,
        )

        with st.form("lead_form", clear_on_submit=True):
            st.subheader(T["customer_info"])
            service = st.selectbox(T["service_needed"], T["service_options"])
            name = st.text_input(T["name"], placeholder="Jordan Smith")
            phone = st.text_input(T["phone"], placeholder="(555) 123-4567")
            email = st.text_input(T["email"], placeholder="name@example.com")
            address = st.text_input(T["address"], placeholder="123 Main St, Denver, CO")
            details = st.text_area(T["details"], placeholder="Tell us what you need help with...")

            st.subheader(T["appointment_info"])
            urgency = st.selectbox(
                T["urgency"],
                [T["urgency_low"], T["urgency_medium"], T["urgency_high"]],
            )
            preferred_date = st.date_input(
                T["preferred_date"],
                min_value=datetime.today().date(),
            )
            preferred_time = st.selectbox(
                T["preferred_time"],
                [
                    (
                        datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
                        + timedelta(minutes=30 * i)
                    ).strftime("%I:%M %p")
                    for i in range(18)
                ],
            )

            st.subheader(T["history_info"])
            st.write(f"1. {T['history_1']}: {st.session_state['language']}")
            st.write(f"2. {T['history_2']}: {service}")
            st.write(f"3. {T['history_3']}: {urgency}")
            st.write(f"4. {T['history_4']}: {preferred_date} at {preferred_time}")

            submitted = st.form_submit_button(T["submit"], use_container_width=True)

    with right:
        st.markdown(
            f"<div class='section-title'>{T['summary_title']}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div class='info-card'>
                <h4>{service if 'service' in locals() else 'Preview'}</h4>
                <p><strong>{T['language']}:</strong> {st.session_state['language']}</p>
                <p><strong>{T['urgency']}:</strong> {urgency if 'urgency' in locals() else ''}</p>
                <p><strong>{T['preferred_date']}:</strong> {preferred_date if 'preferred_date' in locals() else ''}</p>
                <p><strong>{T['preferred_time']}:</strong> {preferred_time if 'preferred_time' in locals() else ''}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if submitted:
        if not name.strip() or not phone.strip() or not service.strip():
            st.error(
                "Please complete name, phone, and service."
                if st.session_state["language"] == "English"
                else "Complete el nombre, teléfono y servicio."
            )
        else:
            lead_id = save_lead(
                language=st.session_state["language"],
                service=service,
                name=name.strip(),
                phone=phone.strip(),
                email=email.strip(),
                address=address.strip(),
                details=details.strip(),
                urgency=urgency,
                preferred_date=str(preferred_date),
                preferred_time=preferred_time,
            )

            save_history(lead_id, T["history_1"], st.session_state["language"])
            save_history(lead_id, T["history_2"], service)
            save_history(lead_id, T["history_3"], urgency)
            save_history(lead_id, T["history_4"], f"{preferred_date} {preferred_time}")

            st.success(T["success"])

            phone_link = clean_phone(phone)
            address_link = quote_plus(address)

            st.markdown(
                f"<div class='section-title'>{T['confirm_title']}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(f"### {T['structured_output']}")
            st.markdown(f"**{T['name']}:** {name}")
            st.markdown(f"**{T['service_needed']}:** {service}")
            st.markdown(f"**{T['urgency']}:** {urgency}")
            st.markdown(f"**{T['preferred_date']}:** {preferred_date}")
            st.markdown(f"**{T['preferred_time']}:** {preferred_time}")
            st.markdown(f"**{T['phone']}:** [{phone}](tel:{phone_link})")

            if email:
                st.markdown(f"**{T['email']}:** [{email}](mailto:{email})")
            if address:
                st.markdown(
                    f"**{T['address']}:** [{address}](https://maps.google.com/?q={address_link})"
                )
            if details:
                st.markdown(f"**{T['details']}:** {details}")

elif page == T["nav_admin"]:
    st.subheader(T["admin_title"])
    st.write(T["admin_subtitle"])

    if st.button(T["refresh"]):
        st.rerun()

    leads_df = fetch_leads()
    history_df = fetch_history()

    st.markdown(f"### {T['lead_table']}")
    if leads_df.empty:
        st.warning(T["empty"])
    else:
        st.dataframe(leads_df, use_container_width=True)
        st.markdown("### Lead Cards")
        for _, row in leads_df.head(10).iterrows():
            phone_link = clean_phone(str(row["phone"]))
            address_text = str(row["address"]) if pd.notna(row["address"]) else ""
            address_link = quote_plus(address_text)

            with st.container(border=True):
                st.markdown(f"**{row['name']}** — {row['service']}")
                st.write(f"Language: {row['language']}")
                st.write(f"Urgency: {row['urgency']}")
                st.write(
                    f"Preferred appointment: {row['preferred_date']} at {row['preferred_time']}"
                )
                st.markdown(f"[{T['click_phone']}](tel:{phone_link})")

                if pd.notna(row["email"]) and str(row["email"]).strip():
                    st.markdown(f"[{T['click_email']}](mailto:{str(row['email'])})")
                if address_text.strip():
                    st.markdown(
                        f"[{T['click_address']}](https://maps.google.com/?q={address_link})"
                    )
                if pd.notna(row["details"]) and str(row["details"]).strip():
                    st.write(str(row["details"]))

    st.markdown(f"### {T['history_table']}")
    if history_df.empty:
        st.warning(T["empty"])
    else:
        st.dataframe(history_df, use_container_width=True)
