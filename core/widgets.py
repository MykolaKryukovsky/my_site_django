from typing import Any, Dict, Optional
from django.forms import widgets


class IconSelectWidget(widgets.Select):
    """
    Кастомний селект, який динамічно додає атрибути іконок Font Awesome
    до кожної опції вибору технології.
    """

    def create_option(
            self, name: str, value: Any, label: str, selected: bool,
            index: int, subindex: Optional[int] = None, attrs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        option = super().create_option(name, value, label, selected, index, subindex, attrs)

        icons_map = {
            'python': 'fa-brands fa-python',
            'js': 'fa-brands fa-js',
            'design': 'fa-solid fa-palette'
        }

        tech_key = str(value).lower()
        if tech_key in icons_map:
            option['attrs']['data-icon'] = icons_map[tech_key]

        return option
