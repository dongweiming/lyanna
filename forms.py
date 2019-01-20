import markupsafe
from sanic_wtf import SanicForm as _SanicForm, FileAllowed, FileRequired
from wtforms import (
    PasswordField, StringField, SubmitField, BooleanField,
    SelectField, SelectMultipleField, TextAreaField, FileField)
from wtforms.widgets import HiddenInput
from wtforms.validators import DataRequired


class SwitchField(SelectField):
    ...


class SanicForm(_SanicForm):
    def hidden_tag(self, *fields):
        def hidden_fields(fields):
            for f in fields:
                if isinstance(f, str):
                    f = getattr(self, f, None)

                if f is None or not isinstance(f.widget, HiddenInput):
                    continue

                yield f

        return markupsafe.Markup(
            u'\n'.join(str(f) for f in hidden_fields(fields or self))
        )

    def validate(self, extra_validators=None):
        self._errors = None
        success = True
        for name, field in self._fields.items():
            if field.type in ('SelectField', 'SelectMultipleField'):
                continue
            if extra_validators is not None and name in extra_validators:
                extra = extra_validators[name]
            else:
                extra = tuple()
            if not field.validate(self, extra):
                success = False
        return success


class LoginForm(SanicForm):
    name = StringField('Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class UserForm(SanicForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
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
    author_id = SelectField('AuthorId', default='', validators=[DataRequired()])  # noqa
    status = SwitchField('Published', choices=[('on', 1), ('off', 0)],
                         default='on')
    is_page = BooleanField('IsPage', default=False)
    submit = SubmitField('Submit')


class ProfileForm(SanicForm):
    avatar = FileField('Avatar', validators=[
        FileRequired(), FileAllowed('bmp gif jpg jpeg png'.split())])
    avatar_path = StringField('AvatarPath', default='')
    intro = StringField('Intro', default='')
    github_url = StringField('Github URL', default='')
    linkedin_url = StringField('Linkedin URL', default='')
    submit = SubmitField('Submit')
