from typing import List, Callable

import numpy as np
import torch
from transformers.tokenization_utils import PreTrainedTokenizer, BatchEncoding
from transformers import BertForMaskedLM


class BertScorerSentence:
    """Class for scoring all sentences in MLM."""

    def __init__(
            self,
            model: BertForMaskedLM,
            tokenizer: PreTrainedTokenizer,
            device: int = -1
    ):
        """Init object.

        :param model: Bert model for MLM from transformers library
        :param tokenizer: tokenizer for Bert model
        :param device: id of device
        """
        self.device = torch.device('cpu' if device < 0 else f'cuda:{device}')
        self.model = model.to(device=self.device)
        self.tokenizer = tokenizer

    def __call__(self, sentences: List[str],
                 batch_size: int = 64,
                 agg_func: Callable = np.mean) -> List[float]:
        """
        Make scoring for all hypotheses.

        :param sentences: list of sentences
        :param batch_size: max size of batch
        :param agg_func: how to aggregate all log probs for sentence

        :returns: scores for each sentence
        """
        tokenized_sentences = self.tokenizer(
            sentences,
            add_special_tokens=True,
            padding=True,
            truncation='only_first',
        )

        # try to place mask token at each reasonable position
        scores = [list() for i in range(len(sentences))]
        sentences_lengths = np.sum(tokenized_sentences['attention_mask'],
                                   axis=-1)
        for mask_index in range(max(sentences_lengths)):
            # create valid BatchEncoding object to make scoring
            # find indices of sentences to make scoring
            # some sentences can be already finished
            indices_to_process = [
                i for i in range(len(sentences))
                if mask_index < sentences_lengths[i]
            ]

            input_dict = {}
            input_dict['input_ids'] = torch.tensor(
                [
                    tokenized_sentences['input_ids'][i][:mask_index]
                    + [self.tokenizer.mask_token_id]
                    + tokenized_sentences['input_ids'][i][mask_index + 1:]
                    for i in indices_to_process
                ], dtype=torch.long, device=self.device
            )
            input_dict['attention_mask'] = torch.tensor(
                [
                    tokenized_sentences['attention_mask'][i]
                    for i in indices_to_process
                ], dtype=torch.long, device=self.device
            )
            input_dict['token_type_ids'] = torch.tensor(
                [
                    tokenized_sentences['token_type_ids'][i]
                    for i in indices_to_process
                ],
                dtype=torch.long, device=self.device
            )
            current_scores = []
            candidates = [
                tokenized_sentences['input_ids'][i][mask_index]
                for i in indices_to_process
            ]
            num_batches = int(np.ceil(len(indices_to_process) / batch_size))
            for i in range(num_batches):
                lower_idx = batch_size*i
                upper_idx = batch_size*(i+1)
                input_batch_dict = {}
                input_batch_dict['input_ids'] = input_dict['input_ids'][
                        lower_idx:upper_idx, :
                ]
                input_batch_dict['attention_mask'] = input_dict['attention_mask'][
                        lower_idx:upper_idx, :
                ]
                input_batch_dict['token_type_ids'] = input_dict['token_type_ids'][
                        lower_idx:upper_idx, :
                ]
                model_input_batch = BatchEncoding(input_batch_dict)
                candidates_batch = candidates[lower_idx:upper_idx]
                batch_scores = (
                    self._score_contexts(
                        model_input_batch, mask_index, candidates_batch
                    )
                )
                current_scores += batch_scores
            for idx, score in zip(indices_to_process, current_scores):
                scores[idx].append(score)
        agg_scores = [agg_func(score_list) for score_list in scores]
        return agg_scores

    def _score_contexts(
            self, model_input: BatchEncoding, mask_index: int,
            candidates: List[int],
    ) -> List[float]:
        """
        Scoring of context.

        :param model_input: source sentences with [MASK] token at one position
        :param mask_index: index of [MASK] tokens for all sentences
        :param candidates: input_id of each candidate

        :returns: results of scoring
        """
        with torch.no_grad():
            model_output = self.model(**model_input)[0]
            log_probs = torch.nn.functional.log_softmax(
                model_output[:, mask_index, :], dim=-1
            )
            scores = log_probs[torch.arange(len(candidates)), candidates]
        return scores.tolist()
