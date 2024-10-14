# app/schemas/auth_schemas.py

from marshmallow import Schema, fields, validate


class RegisterSchema(Schema):
    email = fields.Email(
        required=True, error_messages={"required": "Email is required."}
    )
    password = fields.String(
        required=True,
        validate=validate.Length(min=6),
        error_messages={
            "required": "Password is required.",
            "validate": "Password must be at least 6 characters long.",
        },
    )
    first_name = fields.String(
        required=True,
        validate=validate.Regexp(
            r"^[a-zA-Z]+$", error="First name must contain only letters."
        ),
        error_messages={"required": "First name is required."},
    )
    last_name = fields.String(
        required=True,
        validate=validate.Regexp(
            r"^[a-zA-Z]+$", error="Last name must contain only letters."
        ),
        error_messages={"required": "Last name is required."},
    )
    username = fields.String(
        required=True,
        validate=validate.Length(min=3),
        error_messages={
            "required": "Username is required.",
            "validate": "Username must be at least 3 characters long.",
        },
    )


class LoginSchema(Schema):
    username = fields.String(
        required=True, error_messages={"required": "Username is required."}
    )
    password = fields.String(
        required=True, error_messages={"required": "Password is required."}
    )


class ResetPasswordSchema(Schema):
    email = fields.Email(
        required=True, error_messages={"required": "Email is required."}
    )


class ChangePasswordSchema(Schema):
    old_password = fields.String(
        required=True, error_messages={"required": "Old password is required."}
    )
    new_password = fields.String(
        required=True,
        validate=validate.Length(min=6),
        error_messages={
            "required": "New password is required.",
            "validate": "New password must be at least 6 characters long.",
        },
    )


class DeactivateAccountSchema(Schema):
    username = fields.String(
        required=True, error_messages={"required": "Username is required."}
    )
    password = fields.String(
        required=True, error_messages={"required": "Password is required."}
    )
