from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .apps import ChooseWordConfig


class BertTestItemSerializer(serializers.Serializer):
    """Item of test to solve."""
    text_parts = serializers.ListField(
        child=serializers.CharField(allow_blank=True)
    )
    candidates = serializers.ListField(child=serializers.ListField(
        child=serializers.CharField(allow_blank=True)
    ))

    def validate(self, data):
        """Make validation, that requires many fields."""
        if len(data['text_parts']) != len(data['candidates']) + 1:
            raise ValidationError('Wrong lengths of input!')

        return data

    def validate_text_parts(self, value):
        """Check validity of test parts."""
        tokenizer = ChooseWordConfig.tokenizer

        tokenized_text_parts = tokenizer(
            value,
            add_special_tokens=False,
            padding=False,
            truncation='do_not_truncate',
        )['input_ids']
        for tokenized_text_part in tokenized_text_parts:
            # validate absense of [UNK] tokens
            if tokenized_text_part.count(tokenizer.unk_token_id):
                raise ValidationError(
                    'There should not be [UNK] tokens in the text, '
                    'you probably typed something non-typical!'
                )

            # validate absense of [MASK]-tokens
            if tokenized_text_part.count(tokenizer.mask_token_id):
                raise ValidationError(
                    'There should not be [MASK] tokens in the text!'
                )

        return value

    def validate_candidates(self, value):
        """Check validity of list of candidates."""
        for gap_candidates in value:
            # validate that there are no empty list of candidates
            if len(gap_candidates) < 2:
                raise ValidationError(
                    'There should be at least 2 candidates for each gap!'
                )

            # validate that there are no duplicates
            if len(set(gap_candidates)) != len(gap_candidates):
                raise ValidationError(
                    'There should not be duplicate candidates!'
                )

            # validate that there are no empty candidates
            for candidate in gap_candidates:
                if len(candidate) == 0:
                    raise ValidationError(
                        'There should not be empty candidates!'
                    )

            # tokenize candidates for further validation
            tokenizer = ChooseWordConfig.tokenizer
            tokenized_candidates = tokenizer(
                gap_candidates,
                add_special_tokens=False,
                padding=False,
                truncation='do_not_truncate',
            )['input_ids']

            # validate absense of [UNK] tokens
            for tokenized_candidate in tokenized_candidates:
                if tokenized_candidate.count(tokenizer.unk_token_id):
                    raise ValidationError(
                        'There should not be [UNK] tokens in the text, '
                        'you probably typed something non-typical!'
                    )

            # validate absense of [MASK]-tokens
            for tokenized_candidate in tokenized_candidates:
                if tokenized_candidate.count(tokenizer.mask_token_id):
                    raise ValidationError(
                        'There should not be [MASK] tokens in the text!'
                    )

            # validate candidates are not too big
            max_len = max(
                [len(x) for x in tokenized_candidates]
            )
            if max_len > ChooseWordConfig.max_bert_candidate:
                raise ValidationError(
                    "Too big candidate is used!"
                )

        return value
