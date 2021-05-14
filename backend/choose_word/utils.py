import re
from typing import List

import numpy as np

from nltk import download
from nltk import sent_tokenize

from .apps import ChooseWordConfig


download('punkt')


def process_text_bert(
        text_parts: List[str], candidates: List[List[str]]
) -> List[List[float]]:
    """Process all gaps with candidates.

    :param text_parts: pieces of texts between gaps, length: n+1
    :param candidates: list of candidates for each gap, length: n

    :returns: percent of each candidate in each gap
    """
    # check input on correctness
    if len(text_parts) != len(candidates) + 1:
        raise ValueError('Wrong lengths of input!')

    # divide task by sentences
    # replace each gap by [UNK]-token and join all pieces of text
    unk_token = ChooseWordConfig.tokenizer.unk_token
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
    """Process all gaps with candidates within sentence.

    :param sentence: sentence to process
    :param candidates: list of candidates for each gap

    :returns: percent of each candidate in each gap
    """
    unk_token = ChooseWordConfig.tokenizer.unk_token
    mask_token = ChooseWordConfig.tokenizer.mask_token

    # process each gap separately
    results = []
    pattern = unk_token.replace('[', '\[').replace(']', '\]')
    for i, match in enumerate(re.finditer(pattern, sentence)):
        left, right = match.span()
        # TODO: add processing too long sentences (needs tokenization)
        sentence_to_test = f'{sentence[:left]}{mask_token}{sentence[right:]}'
        try:
            scores = ChooseWordConfig.bert_scorer_correction(
                [sentence_to_test], [candidates[i]]
            )[0]
            # normalize scores
            normalized_scores = np.exp([np.mean(x) for x in scores])
            percents = normalized_scores / np.sum(normalized_scores)
            results.append(percents)
        except ValueError as e:
            if str(e).startswith('There should be exactly one [MASK]'):
                raise ValueError(
                    'There should not be [UNK] tokens in the text!'
                )
            else:
                raise e
    return results
