SUPPORTED_LANGUAGE_CHOICES = (
    ("en", "English"),
    ("de", "German"),
    ("ar", "Arabic"),
    ("tr", "Turkish"),
    ("fa", "Farsi"),
    ("fr", "French"),
    ("es", "Spanish"),
    ("pt", "Portuguese"),
    ("nl", "Dutch"),
    ("zh", "Chinese"),
)

SUPPORTED_LANGUAGE_CODES = {code for code, _ in SUPPORTED_LANGUAGE_CHOICES}
DEFAULT_LANGUAGE_CODE = "en"
RTL_LANGUAGE_CODES = {"ar", "fa"}


def normalize_language_code(language_code):
    code = (language_code or "").lower().strip()
    return code if code in SUPPORTED_LANGUAGE_CODES else DEFAULT_LANGUAGE_CODE


def is_rtl_language(language_code):
    return normalize_language_code(language_code) in RTL_LANGUAGE_CODES


def translated_field_name(base_name, language_code):
    return f"{base_name}_{normalize_language_code(language_code)}"


def translation_field_names(base_names=("title", "description")):
    field_names = []
    for code, _label in SUPPORTED_LANGUAGE_CHOICES:
        for base_name in base_names:
            field_names.append(f"{base_name}_{code}")
    return field_names


def site_language_options():
    return [
        {
            "code": code,
            "label": label,
            "direction": "rtl" if code in RTL_LANGUAGE_CODES else "ltr",
        }
        for code, label in SUPPORTED_LANGUAGE_CHOICES
    ]
