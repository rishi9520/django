import streamlit as st


def render_support_page(school_id, data_manager):
    """Renders the customer support page with a WhatsApp link."""

    # Aapka MSG91 par register kiya hua WhatsApp number
    SUPPORT_WHATSAPP_NUMBER = "917599377142"

    # Pre-filled message (Ismein humne keyword 'Support' daal diya hai)
    PRE_FILLED_MESSAGE = "Support"

    # WhatsApp "Click to Chat" link banayein
    # URL encoding zaroori hai taaki space etc. sahi se handle ho
    from urllib.parse import quote

    whatsapp_url = (
        f"https://wa.me/{SUPPORT_WHATSAPP_NUMBER}?text={quote(PRE_FILLED_MESSAGE)}"
    )

    st.markdown(
        """
        <style>
        .support-container {
            max-width: 800px;
            margin: 2rem auto;
            padding: 2rem;
            background-color: #f9fafb;
            border-radius: 12px;
            text-align: center;
            border: 1px solid #e5e7eb;
        }
        .support-header {
            font-size: 2.5rem;
            font-weight: 700;
            color: #1E3A8A;
            margin-bottom: 1rem;
        }
        .support-subheader {
            font-size: 1.1rem;
            color: #475569;
            margin-bottom: 2rem;
            line-height: 1.6;
        }
        .whatsapp-button {
            display: inline-flex;
            align-items: center;
            padding: 14px 28px;
            background-color: #25D366;
            color: white;
            border-radius: 50px;
            text-decoration: none;
            font-weight: 600;
            font-size: 1.1rem;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            box-shadow: 0 4px 15px rgba(37, 211, 102, 0.2);
        }
        .whatsapp-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 7px 20px rgba(37, 211, 102, 0.3);
        }
        .whatsapp-icon {
            width: 24px;
            height: 24px;
            margin-right: 12px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="support-container">
            <h1 class="support-header">Need Help?</h1>
            <p class="support-subheader">
                Facing an issue or have a question? Our support team is just a message away. 
                Click the button below to start a conversation with us on WhatsApp.
            </p>
            <a href="{whatsapp_url}" target="_blank" class="whatsapp-button">
                <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" class="whatsapp-icon">
                Chat with Support on WhatsApp
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "ℹ️ Clicking the button will open WhatsApp with a pre-filled message 'Support' to initiate the chat with our support bot."
    )
