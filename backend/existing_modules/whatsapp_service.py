import requests
import json
import time

# ==============================================================================
# === MSG91 KI DETAILS YAHAN DAALEIN ===
# ==============================================================================

# # Aapka MSG91 ka Authentication Key
AUTH_KEY = "444852AYpUlDhd685ec94eP1"

# Aapka WhatsApp number jo MSG91 par register hai (e.g., '917599377142')
INTEGRATED_NUMBER = "917599377142"

# Har template ke liye Template Name
TEMPLATE_ARRANGEMENT = "teacher_daily_arrangements"
TEMPLATE_MANUAL = "manual_teacher_arrangement"
TEMPLATE_ABSENT = "teacher_absence_confirmation"

# ==============================================================================


def _send_msg91_request(payload):
    """
    Internal function to send API request to MSG91 using the correct Bulk Template API endpoint.
    Includes retry logic for better reliability.
    """
    # Sahi API Endpoint (Bulk wala)
    url = "https://api.msg91.com/api/v5/whatsapp/whatsapp-outbound-message/bulk/"
    headers = {"authkey": AUTH_KEY, "Content-Type": "application/json"}

    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(
                f"DEBUG: Sending MSG91 Bulk Template payload (Attempt {attempt + 1}/{max_retries}): {json.dumps(payload, indent=2)}"
            )
            response = requests.post(
                url, headers=headers, data=json.dumps(payload), timeout=30
            )
            response.raise_for_status()

            print(
                f"SUCCESS: MSG91 API call successful on attempt {attempt + 1}. Response: {response.text}"
            )
            return True

        except requests.exceptions.Timeout as e:
            print(f"WARNING: MSG91 Timeout on attempt {attempt + 1}. Error: {e}")
            if attempt == max_retries - 1:
                print("ERROR: MSG91 request failed after all retries due to timeout.")
                return False
            time.sleep(5 * (attempt + 1))

        except requests.exceptions.RequestException as e:
            print(
                f"ERROR: Failed to send MSG91 message on attempt {attempt + 1}. Error: {e}"
            )
            if "response" in locals() and hasattr(response, "text"):
                print(f"Response Body from MSG91: {response.text}")

            if "response" in locals() and response.status_code in [401, 403, 400]:
                print(
                    "ERROR: Unrecoverable client error (e.g., Invalid AuthKey or malformed JSON). Aborting retries."
                )
                return False

            if attempt == max_retries - 1:
                print("ERROR: MSG91 request failed after all retries.")
                return False
            time.sleep(5 * (attempt + 1))

    return False


def send_arrangement_notification(
    replacement_teacher_name,
    replacement_teacher_phone,
    arrangement_details_list,
    school_name,
):
    """Auto-arrangement ka message bhejta hai (SAHI FORMAT MEIN)."""
    if not str(replacement_teacher_phone).strip():
        print("ERROR (Arrangement): Replacement teacher phone number is missing.")
        return

    # Saare arrangement details ko ek hi string me jodo
    arrangement_text = "\\n".join(
        arrangement_details_list
    )  # Use \\n for newlines in MSG91

    # Sahi payload banayein
    payload = {
        "integrated_number": INTEGRATED_NUMBER,
        "content_type": "template",
        "payload": {
            "messaging_product": "whatsapp",
            "type": "template",
            "template": {
                "name": TEMPLATE_ARRANGEMENT,
                "language": {"code": "en"},
                "to_and_components": [
                    {
                        "to": [
                            f"91{str(replacement_teacher_phone).strip()}"
                        ],  # Country code ke saath
                        "components": {
                            "body_1": {
                                "type": "text",
                                "value": replacement_teacher_name,
                            },
                            "body_2": {"type": "text", "value": "today"},
                            "body_3": {"type": "text", "value": arrangement_text},
                            "body_4": {"type": "text", "value": school_name},
                        },
                    }
                ],
            },
        },
    }
    _send_msg91_request(payload)


def send_manual_arrangement_notification(
    teacher_name, teacher_phone, manual_arrangement_detail, school_name
):
    """Manual arrangement ka message bhejta hai (SAHI FORMAT MEIN)."""
    if not str(teacher_phone).strip():
        print("ERROR (Manual): Teacher phone number is missing.")
        return

    payload = {
        "integrated_number": INTEGRATED_NUMBER,
        "content_type": "template",
        "payload": {
            "messaging_product": "whatsapp",
            "type": "template",
            "template": {
                "name": TEMPLATE_MANUAL,
                "language": {"code": "en"},
                "to_and_components": [
                    {
                        "to": [f"91{str(teacher_phone).strip()}"],
                        "components": {
                            "body_1": {"type": "text", "value": teacher_name},
                            "body_2": {"type": "text", "value": "today"},
                            "body_3": {
                                "type": "text",
                                "value": manual_arrangement_detail,
                            },
                            "body_4": {"type": "text", "value": school_name},
                        },
                    }
                ],
            },
        },
    }
    _send_msg91_request(payload)


def send_absent_confirmation(teacher_name, teacher_phone, school_name):
    """Absent mark hone ka confirmation message bhejta hai (SAHI FORMAT MEIN)."""
    if not str(teacher_phone).strip():
        print("ERROR (Absent): Teacher phone number is missing.")
        return

    payload = {
        "integrated_number": INTEGRATED_NUMBER,
        "content_type": "template",
        "payload": {
            "messaging_product": "whatsapp",
            "type": "template",
            "template": {
                "name": TEMPLATE_ABSENT,
                "language": {"code": "en"},
                "to_and_components": [
                    {
                        "to": [f"91{str(teacher_phone).strip()}"],
                        "components": {
                            "body_1": {"type": "text", "value": teacher_name},
                            "body_2": {"type": "text", "value": "today"},
                            "body_3": {"type": "text", "value": school_name},
                        },
                    }
                ],
            },
        },
    }
    _send_msg91_request(payload)
# test line to trigger git