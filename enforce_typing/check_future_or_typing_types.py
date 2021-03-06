"""Module to enforce strict typing for functions decorated using the Typing module."""
from __future__ import annotations

import re

from .exceptions import EnforcedTypingError
from .type_parser import data_type_from_string


class CheckTyping:
    """Check type annotations for functions decorated with Typing type hints."""

    def __init__(
        self,
        arg_name: str,
        arg_type: any,
        arg_value: any,
        expected_type: any,
    ) -> CheckTyping:
        """
        Create an instance of CheckTyping.

        Args:
            arg_name: str
                The name of the argument.

            arg_type: any
                The datatype of the argument.

            arg_value: any
                The value of the argument.

            expected_type: str
                The datatype type hinted at the
                function definition.
        """
        self.arg_name = arg_name
        self.arg_type = arg_type
        self.arg_value = arg_value
        self.expected_type = expected_type

    def _check_typing_dict(self, sub_types: list[any]):
        """
        Check that the typed values for a dict match the values provided.

        Args:
            sub_types: List[any]
                The specified types within the
                typing Dict type hint.

        Raises: EnforcedTypingError
            If the data does not match
            the datatype of the type
            hint.
        """
        typed_key, typed_value = sub_types
        for key, value in self.arg_value.items():
            if typed_key != type(key) or typed_value != type(value):
                raise EnforcedTypingError(
                    f"'{self.arg_name}' has a key type of {type(key).__qualname__} "
                    f"and a value type of {type(value).__qualname__}.\n"
                    f"Should have a key type of {typed_key.__qualname__} "
                    f"and a value type of {typed_value.__qualname__}."
                )

    def _check_typing_list(self, sub_types: list[any]):
        """
        Check that the typed value for a list match the values provided.

        Args:
            sub_types: List[any]
                The specified type within the
                typing List type hint.

        Raises: EnforcedTypingError
            If the data does not match
            the datatype of the type
            hint.
        """
        for i, item in enumerate(self.arg_value):
            if not isinstance(item, sub_types[0]):
                raise EnforcedTypingError(
                    f"'{self.arg_name}' has a {type(item).__qualname__} at index {i}"
                    f", but should be {sub_types[0].__qualname__}."
                )

    def _check_typing_tuple(self, sub_types: list[any]):
        """
        Check that the typed values for a tuple match the values provided.

        Args:
            sub_types: List[any]
                The specified types within the
                typing Tuple type hint.

        Raises: EnforcedTypingError
            If the data does not match
            the datatype of the type
            hint.
        """
        if len(self.arg_value) != len(sub_types):
            raise EnforcedTypingError(
                f"'{self.arg_name}' has a length of {len(self.arg_value)}"
                f", but should be a length of {len(sub_types)}."
            )

        for i, (item, sub_type) in enumerate(zip(self.arg_value, sub_types)):
            if not isinstance(item, sub_type):
                raise EnforcedTypingError(
                    f"'{self.arg_name}' has a {type(item).__qualname__} at index {i}"
                    f", but should be {sub_type.__qualname__}."
                )

    @staticmethod
    def split_typing_sub_types(sub_types: str) -> list[any]:
        """
        Convert sub_types from a string to a list.

        Args:
            sub_types: str
                A string of sub types joined
                from a typing type hint.

        Returns: List[any]
            A list of sub types.
        """
        cleaned_sub_types: list[any] = []
        name_space: dict[str, any] = {}

        for item in (
            sub_types.replace("[", "").replace("]", "").replace(" ", "").split(",")
        ):
            cleaned_sub_types.append(
                data_type_from_string(
                    data_type=item,
                    name_space=name_space,
                )
            )

        return cleaned_sub_types

    def _raise_error(self):
        """Raise an EnforcedTypingError."""
        raise EnforcedTypingError(
            f"'{self.arg_name}' is a {self.arg_type.__qualname__}"
            f", but should be {self.expected_type.__qualname__}."
        )

    def _get_types(self):
        """Return the base and sub_types of the argument."""
        print(self.expected_type)
        expected_type = self.expected_type.split("typing.")
        result = re.search(r"([A-z].*)(\[.*])", expected_type[len(expected_type) - 1])
        base_type: str = result.group(1)
        sub_types: list[any] = self.split_typing_sub_types(result.group(2))

        return (base_type, sub_types)

    def _test_tuple(self, sub_types):
        """Raise an exception if the argument is not a tuple."""
        self.__setattr__("expected_type", tuple)
        if self.arg_type == tuple:
            self._check_typing_tuple(sub_types=sub_types)
        else:
            self._raise_error()

    def _test_dict(self, sub_types):
        """Raise an exception if the argument is not a dict."""
        self.__setattr__("expected_type", dict)
        if self.arg_type == dict:
            self._check_typing_dict(sub_types=sub_types)
        else:
            self._raise_error()

    def _test_list(self, sub_types):
        """Raise an exception if the argument is not a list."""
        self.__setattr__("expected_type", list)
        if self.arg_type == list:
            self._check_typing_list(sub_types=sub_types)
        else:
            self._raise_error()

    def validate(self):
        """
        Test to see if type hints used with typing types are correct.

        Raises: EnforcedTypingError
            If the data does not match
            the datatype of the type
            hint.
        """
        try:
            base_type, sub_types = self._get_types()
            if base_type.lower() == "dict":
                self._test_dict(sub_types)

            elif base_type.lower() == "list":
                self._test_list(sub_types)

            elif base_type.lower() == "tuple":
                self._test_tuple(sub_types)

        except AttributeError:
            return
