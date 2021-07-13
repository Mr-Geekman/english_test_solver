from typing import List

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .apps import ChooseWordConfig


def validator_no_unk_mask_tokens(tokenizer):
    def validate_no_unk_mask_tokens(string_to_check):
        """Check absense of [UNK] and [MASK] tokens in value.

        :param string_to_check: string to validate

        :returns: validated value
        """
        tokenized_string = tokenizer(
            string_to_check,
            add_special_tokens=False,
            padding=False,
            truncation='do_not_truncate',
        )['input_ids']
        # validate absense of [UNK] tokens
        if tokenizer.unk_token_id is not None:
            if tokenized_string.count(tokenizer.unk_token_id):
                raise ValidationError(
                    f'There should not be {tokenizer.unk_token} '
                    f'tokens in the text, '
                    f'you probably typed something non-typical!'
                )

        # validate absense of [MASK]-tokens
        if tokenizer.mask_token_id is not None:
            if tokenized_string.count(tokenizer.mask_token_id):
                raise ValidationError(
                    f'There should not be {tokenizer.mask_token} '
                    f'tokens in the text!'
                )

        return string_to_check

    return validate_no_unk_mask_tokens


def validate_candidates_numbers(list_candidates: List[str]):
    """Check that there are good number of candidates.

    :param list_candidates: list of strings to validate

    :returns: validated value
    """
    # validate that there are no empty list of candidates
    if len(list_candidates) < 2:
        raise ValidationError(
            'There should be at least 2 candidates for each gap!'
        )

    # validate that there are no duplicates
    if len(set(list_candidates)) != len(list_candidates):
        raise ValidationError(
            'There should not be duplicate candidates!'
        )

    # validate that there are no empty candidates
    for candidate in list_candidates:
        if len(candidate) == 0:
            raise ValidationError(
                'There should not be empty candidates!'
            )

    return list_candidates


def validate_candidates_sizes(list_candidates: List[str]):
    """Check that there are small enough candidates.

    :param list_candidates: list of strings to validate

    :returns: validated value
    """
    # tokenize candidates for further validation
    tokenizer = ChooseWordConfig.bert_tokenizer
    tokenized_candidates = tokenizer(
        list_candidates,
        add_special_tokens=False,
        padding=False,
        truncation='do_not_truncate',
    )['input_ids']

    # validate candidates are not too big
    max_len = max(
        [len(x) for x in tokenized_candidates]
    )
    if max_len > ChooseWordConfig.max_bert_candidate:
        raise ValidationError(
            "Too big candidate is used!"
        )

    return list_candidates


class BertTestItemSerializer(serializers.Serializer):
    """Item of test to solve using BERT algorightm."""
    text_parts = serializers.ListField(
        child=serializers.CharField(
            allow_blank=True,
            validators=[
                validator_no_unk_mask_tokens(ChooseWordConfig.bert_tokenizer)
            ]
        ),
    )
    candidates = serializers.ListField(child=serializers.ListField(
        child=serializers.CharField(
            allow_blank=True,
            validators=[
                validator_no_unk_mask_tokens(ChooseWordConfig.bert_tokenizer)
            ]
        ),
        validators=[validate_candidates_numbers, validate_candidates_sizes]
    ))

    def validate(self, data):
        """Make validation, that requires many fields."""
        if len(data['text_parts']) != len(data['candidates']) + 1:
            raise ValidationError('Wrong lengths of input!')

        return data


class GPTTestItemSerializer(serializers.Serializer):
    """Item of test to solve using GPT algorithm."""
    text_parts = serializers.ListField(
        child=serializers.CharField(
            allow_blank=True,
            validators=[
                validator_no_unk_mask_tokens(ChooseWordConfig.gpt_tokenizer)
            ]
        ),
    )
    candidates = serializers.ListField(child=serializers.ListField(
        child=serializers.CharField(
            allow_blank=True,
            validators=[
                validator_no_unk_mask_tokens(ChooseWordConfig.gpt_tokenizer)
            ]
        ),
        validators=[validate_candidates_numbers]
    ))

    def validate(self, data):
        """Make validation, that requires many fields."""
        if len(data['text_parts']) != len(data['candidates']) + 1:
            raise ValidationError('Wrong lengths of input!')

        return data
