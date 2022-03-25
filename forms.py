from __future__ import annotations

from typing import Any, Generator, Tuple, Union

import markupsafe
from sanic.log import logger
from sanic_wtf import SanicForm as _SanicForm
from wtforms import (
    BooleanField, PasswordField, SelectField,
    SelectMultipleField, StringField, SubmitField, TextAreaField,
)
from wtforms.validators import DataRequired
from wtforms.widgets import HiddenInput


class SwitchField(SelectField):
    ...


class SanicForm(_SanicForm):
    def hidden_tag(self, *fields):
        def hidden_fields(
                fields: Union[Tuple[Any, ...], SanicForm]) -> Generator:
            for f in fields:
                if isinstance(f, str):
                    f = getattr(self, f, None)

                if f is None or not isinstance(f.widget, HiddenInput):
                    continue

                yield f

        return markupsafe.Markup(
            u'\n'.join(str(f) for f in hidden_fields(fields or self))
        )

    def validate(self) -> bool:
        extra_validators = {}
        for name in self._fields:
            if (inline := getattr(self.__class__, 'validate_%s' % name,
                                  None)) is not None:
                extra_validators[name] = [inline]

        self._errors = None
        success = True
        for name, field in self._fields.items():
            if field.type in ('SelectField', 'SelectMultipleField'):
                continue
            if extra_validators is not None and name in extra_validators:
                extra = extra_validators[name]
            else:
                extra = list()
            if not field.validate(self, extra):
                success = False
                logger.info(f'[Validate Fail] {field}')
        return success


class UserForm(SanicForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    avatar = StringField('Email', default='')
    password = PasswordField('Password')
    active = BooleanField('Active')
    submit = SubmitField('Submit')


class PostForm(SanicForm):
    title = StringField('Title', validators=[DataRequired()])
    slug = StringField('Slug')
    summary = StringField('Summary')
    content = TextAreaField('Content', default='')
    can_comment = BooleanField('CanComment', default=True)
    tags = SelectMultipleField('Tags', default=[])
    status = SwitchField('Published', choices=[0, 1], default=1, coerce=int)
    is_page = BooleanField('IsPage', default=False)
    submit = SubmitField('Submit')


class TopicForm(SanicForm):
    slug = StringField('Slug')
    intro = StringField('Intro', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    status = SwitchField('Published', choices=[0, 1], default=1, coerce=int)
