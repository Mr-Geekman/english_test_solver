from typing import List
from copy import copy

import numpy as np

from nltk import download
from nltk import sent_tokenize

from .apps import ChooseWordConfig


download('punkt')


def process_text_bert(
        text_parts: List[str], candidates: List[List[str]]
) -> List[List[float]]:
    """Process all gaps with candidates using BERT algorithm.

    :param text_parts: pieces of texts between gaps, length: n+1
    :param candidates: list of candidates for each gap, length: n

    :returns: percent of each candidate in each gap
    """
    # check input on correctness
    if len(text_parts) != len(candidates) + 1:
        raise ValueError('Wrong lengths of input!')

    # divide task by sentences
    # replace each gap by [UNK]-token and join all pieces of text
    unk_token = ChooseWordConfig.bert_tokenizer.unk_token
    text = f' {unk_token} '.join(text_parts)
    # check if there is no redundant [UNK]-tokens
    # TODO: add escaping [UNK]-tokens and [MASK]-tokens (very unrealistic case)
    if text.count(unk_token) != len(candidates):
        raise ValueError('There should not be [UNK] tokens in the text!')
    # split text by sentences
    sentences = sent_tokenize(text)
    sentences_candidates = []
    cur_cnt = 0
    for sentence in sentences:
        cnt = sentence.count(unk_token)
        sentences_candidates.append(candidates[cur_cnt:cur_cnt+cnt])
        cur_cnt += cnt
    # process each sentence separately
    results = []
    for sentence, sentence_candidates in zip(sentences, sentences_candidates):
        results += process_sentence_bert(sentence, sentence_candidates)

    # return results
    return results


def process_sentence_bert(
        sentence: str, candidates: List[List[str]]
) -> List[List[float]]:
    """Process all gaps with candidates within sentence using BERT algorithm.

    :param sentence: sentence to process
    :param candidates: list of candidates for each gap

    :returns: percent of each candidate in each gap
    """
    # TODO: add processing of bigger context (few sentences)
    # tokenize sentence and candidates
    tokenizer = ChooseWordConfig.bert_tokenizer
    tokenized_sentence = tokenizer(
        sentence,
        add_special_tokens=False,
        padding=False,
        truncation='do_not_truncate',
    )['input_ids']

    results = []
    # process each gap separately
    gap_idx = 0
    for i, token_id in enumerate(tokenized_sentence):
        if token_id != tokenizer.unk_token_id:
            continue
        current_tokenized_sentence = copy(tokenized_sentence)
        current_tokenized_sentence[i] = tokenizer.mask_token_id

        # find maximum length of candidate in each gap
        tokenized_candidates = tokenizer(
            candidates[gap_idx],
            add_special_tokens=False,
            padding=False,
            truncation='do_not_truncate',
        )['input_ids']
        max_len = max([len(x) for x in tokenized_candidates])

        # limit sentence to fit in maximum size
        # -2 added for compensation of rounding, -5 is arbitrary
        radius = ChooseWordConfig.max_bert_size // 2 - max_len // 2 - 2 - 5
        start_idx = max(0, i-radius)
        end_idx = min(len(current_tokenized_sentence), i+radius)
        current_tokenized_sentence = current_tokenized_sentence[
                                     start_idx:end_idx
                                     ]
        current_sentence = tokenizer.decode(current_tokenized_sentence)

        try:
            scores = ChooseWordConfig.bert_scorer_correction(
                [current_sentence], [candidates[gap_idx]]
            )[0]
            # normalize scores
            normalized_scores = np.exp([np.mean(x) for x in scores])
            percents = normalized_scores / np.sum(normalized_scores)
            results.append(percents)
        except ValueError as e:
            if str(e).startswith('There should be exactly one [MASK]'):
                raise ValueError(
                    'There should not be [MASK] tokens in the text!'
                )
            else:
                raise e

        gap_idx += 1

    return results


def process_text_gpt(
        text_parts: List[str], candidates: List[List[str]]
) -> List[List[float]]:
    """Process all gaps with candidates using GPT algorithm.

    :param text_parts: pieces of texts between gaps, length: n+1
    :param candidates: list of candidates for each gap, length: n

    :returns: percent of each candidate in each gap
    """
    # check input on correctness
    if len(text_parts) != len(candidates) + 1:
        raise ValueError('Wrong lengths of input!')

    # divide task by sentences
    # replace each gap by [UNK]-token and join all pieces of text
    unk_token = ChooseWordConfig.gpt_tokenizer.unk_token
    text = f' {unk_token} '.join(text_parts)
    # check if there is no redundant [UNK]-tokens
    # TODO: add escaping [UNK] tokens (very unrealistic case)
    if text.count(unk_token) != len(candidates):
        raise ValueError('There should not be [UNK] tokens in the text!')
    # split text by sentences
    sentences = sent_tokenize(text)
    sentences_candidates = []
    cur_cnt = 0
    for sentence in sentences:
        cnt = sentence.count(unk_token)
        sentences_candidates.append(candidates[cur_cnt:cur_cnt+cnt])
        cur_cnt += cnt
    # process each sentence separately
    results = []
    for sentence, sentence_candidates in zip(sentences, sentences_candidates):
        results += process_sentence_gpt(sentence, sentence_candidates)

    # return results
    return results


def process_sentence_gpt(
        sentence: str, candidates: List[List[str]]
) -> List[List[float]]:
    """Process all gaps with candidates within sentence using GPT algorithm.

    :param sentence: sentence to process
    :param candidates: list of candidates for each gap

    :returns: percent of each candidate in each gap
    """
    # TODO: add processing of bigger context (few sentences)
    # tokenize sentence and candidates
    tokenizer = ChooseWordConfig.gpt_tokenizer
    tokenized_sentence = tokenizer(
        sentence,
        add_special_tokens=False,
        truncation='do_not_truncate',
    )['input_ids']

    results = []
    # process each gap separately
    gap_idx = 0
    for i, token_id in enumerate(tokenized_sentence):
        if token_id != tokenizer.unk_token_id:
            continue

        # tokenize candidates
        tokenized_candidates = tokenizer(
            candidates[gap_idx],
            add_special_tokens=False,
            truncation='do_not_truncate',
        )['input_ids']

        # try to insert each candidate in sentence
        sentences_to_check = []
        for tokenized_candidate in tokenized_candidates:
            current_tokenized_sentence = copy(tokenized_sentence)
            current_tokenized_sentence = (
                current_tokenized_sentence[:i]
                + tokenized_candidate
                + current_tokenized_sentence[i+1:]
            )
            sentences_to_check.append(
                tokenizer.decode(current_tokenized_sentence)
            )

        scores = 1 / np.array(
            ChooseWordConfig.gpt_scorer_sentence(sentences_to_check)
        )
        percents = scores / np.sum(scores)
        results.append(percents)

        gap_idx += 1

    return results
