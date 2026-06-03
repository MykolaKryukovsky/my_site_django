from django.test import SimpleTestCase
from ..widgets import IconSelectWidget


class IconSelectWidgetTest(SimpleTestCase):
    """Набір тестів для перевірки працездатності кастомного віджета IconSelectWidget."""

    def setUp(self) -> None:
        """Ініціалізація віджета перед кожним тестом."""
        self.widget = IconSelectWidget(choices=[
            ('python', 'Python Development'),
            ('js', 'JavaScript'),
            ('design', 'UI/UX Design'),
            ('other', 'Other Technology')
        ])

    def test_create_option_adds_data_icon_attribute(self) -> None:
        """Перевірка, що для відомих технологій автоматично додається HTML-атрибут data-icon."""
        option_python = self.widget.create_option(
            name="tech", value="python", label="Python Development",
            selected=False, index=0
        )

        self.assertIn('data-icon', option_python['attrs'])
        self.assertEqual(option_python['attrs']['data-icon'], 'fa-brands fa-python')

        option_design = self.widget.create_option(
            name="tech", value="design", label="UI/UX Design",
            selected=False, index=2
        )
        self.assertEqual(option_design['attrs']['data-icon'], 'fa-solid fa-palette')

    def test_create_option_no_icon_for_unknown_value(self) -> None:
        """Перевірка, що для невідомих значень атрибут data-icon не додається."""
        option_other = self.widget.create_option(
            name="tech", value="other", label="Other Technology",
            selected=False, index=3
        )

        self.assertNotIn('data-icon', option_other['attrs'])

    def test_create_option_handles_none_and_case_insensitive(self) -> None:
        """Перевірка стійкості віджета до порожніх значень та різного регістру букв."""
        option_caps = self.widget.create_option(
            name="tech", value="PYTHON", label="Python",
            selected=False, index=0
        )
        self.assertEqual(option_caps['attrs']['data-icon'], 'fa-brands fa-python')

        option_none = self.widget.create_option(
            name="tech", value=None, label="Unknown",
            selected=False, index=4
        )
        self.assertNotIn('data-icon', option_none['attrs'])
