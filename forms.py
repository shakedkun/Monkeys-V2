"""
WTForms form definitions – matches the original SubmitForm.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired

import data_store


class SubmitForm(FlaskForm):
    """Task submission form (mirrors the original WTForm)."""

    title = StringField("כותרת", validators=[DataRequired()])
    content = TextAreaField("תוכן", validators=[DataRequired()])
    category = SelectField("קטגוריה", validators=[DataRequired()], coerce=int)
    location = StringField("מיקום", validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category.choices = [
            (c["id"], c["name"]) for c in data_store.categories
        ]
