from repositories.settings_repository import get_setting, set_setting


DEFAULT_CONFIG = {
    "comparative_min_percentage": "18",
    "comparative_max_percentage": "24",
    "budget_days_before_invoice": "10",
    "comparative_budget_days_before": "1",
    "header_image_width_mm": "190",
}


def get_config_value(key: str) -> str:
    default = DEFAULT_CONFIG.get(key, "")
    return get_setting(key, default)


def set_config_value(key: str, value: str) -> None:
    set_setting(key, value)


def get_app_config() -> dict:
    return {
        "comparative_min_percentage": float(
            get_config_value("comparative_min_percentage")
        ),
        "comparative_max_percentage": float(
            get_config_value("comparative_max_percentage")
        ),
        "budget_days_before_invoice": int(
            get_config_value("budget_days_before_invoice")
        ),
        "comparative_budget_days_before": int(
            get_config_value("comparative_budget_days_before")
        ),
        "header_image_width_mm": int(
            get_config_value("header_image_width_mm")
        ),
    }


def initialize_default_config() -> None:
    for key, value in DEFAULT_CONFIG.items():
        current_value = get_setting(key)

        if not current_value:
            set_setting(key, value)


def get_int_config_value(key: str, default: int = 0) -> int:
    value = get_setting(key, str(default))

    try:
        return int(value)
    except ValueError:
        return default


def increment_config_counter(key: str, amount: int = 1) -> None:
    current_value = get_int_config_value(key, 0)
    new_value = current_value + amount

    set_setting(key, str(new_value))