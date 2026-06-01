
from django.forms import widgets


class IconSelectWidget(widgets.Select):
    """Кастомний селект, який додає іконки до опцій."""
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
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
