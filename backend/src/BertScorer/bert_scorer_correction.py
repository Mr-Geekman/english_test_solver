from typing import List, Tuple, Dict

import torch
import torch.nn.functional as F
from transformers.tokenization_utils import PreTrainedTokenizer, BatchEncoding
from transformers import BertForMaskedLM


class BertScorerCorrection:
    """Class for scoring all candidates for correction by BERT model."""

    def __init__(
            self,
            model: BertForMaskedLM,
            tokenizer: PreTrainedTokenizer,
            max_length: int = 512,
            batch_size: int = 16,
            device: int = -1
    ):
        """Init object.

        :param model: Bert model for MLM from transformers library
        :param tokenizer: tokenizer for Bert model
        :param max_length: maximum number of tokens to process
        :param batch_size: size of batch
        :param device: id of device
        """
        self.device = torch.device('cpu' if device < 0 else f'cuda:{device}')
        self.model = model.to(device=self.device)
        self.batch_size = batch_size
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __call__(
            self, sentences: List[str], candidates: List[List[str]]
    ) -> List[List[List[float]]]:
        """Make scoring for candidates for every sentence.

        :param sentences: list of sentences with mask token,
            indicates, where we should place candidates
        :param candidates: list of lists of candidates to score
            for each sentence

        :returns: scoring results for each candidate for each sentence
        """
        tokenized_sentences = self.tokenizer(
            sentences,
            add_special_tokens=True,
            padding=True,
            max_length=self.max_length,
            truncation='longest_first',
        )
        # check, that there is one mask in each sentence
        for sublist in tokenized_sentences['input_ids']:
            if sublist.count(self.tokenizer.mask_token_id) != 1:
                raise ValueError(
                    'There should be exactly one [MASK] token in the text.'
                )

        # find mask index for each sentence
        mask_indexes = [
            x.index(self.tokenizer.mask_token_id)
            for x in tokenized_sentences['input_ids']
        ]

        # group candidates for batching
        candidates_info = self._group_candidates(candidates)

        # make scoring
        score_results = [
            [[] for _ in sentence_candidates]
            for sentence_candidates in candidates
        ]
        current_batch = {'input_ids': [], 'attention_mask': [], 'answers': []}
        indices_to_process = []
        for i in range(len(sentences)):
            mask_index = mask_indexes[i]
            sentence_candidates_info = candidates_info[i]
            # add each group of candidates with the same tokens to the batch
            for j in range(len(sentence_candidates_info['input_ids'])):
                # generate input_ids to score
                current_batch['input_ids'].append(
                    torch.tensor(
                        tokenized_sentences['input_ids'][i][:mask_index]
                        + sentence_candidates_info['input_ids'][j]
                        + tokenized_sentences['input_ids'][i][mask_index + 1:],
                        dtype=torch.long, device=self.device
                    )
                )
                # generate attention_mask to score
                # ignore all tokens except for [MASK]
                current_batch['attention_mask'].append(
                    torch.tensor(
                        tokenized_sentences['attention_mask'][i][:mask_index]
                        + [int(x == self.tokenizer.mask_token_id)
                           for x in sentence_candidates_info['input_ids'][j]]
                        + tokenized_sentences['attention_mask'][i][
                            mask_index + 1:
                          ],
                        dtype=torch.long, device=self.device
                    )
                )
                # generate answers to score
                current_batch['answers'].append(
                    sentence_candidates_info['answers'][j]
                )
                # save indices to further aggregation
                indices_to_process.append(
                    sentence_candidates_info['indices'][j]
                )

                # check do we need to start scoring
                if len(current_batch['input_ids']) > self.batch_size:
                    results_update = self._score_batch(current_batch)
                    current_batch = {
                        'input_ids': [], 'attention_mask': [], 'answers': []
                    }
                    self._update_results(score_results, results_update,
                                         indices_to_process)
                    indices_to_process = []

        # score remain candidates and process them
        if len(current_batch['input_ids']) > 0:
            results_update = self._score_batch(current_batch)
            self._update_results(score_results, results_update,
                                 indices_to_process)

        return score_results

    def _group_candidates(self, candidates: List[List[str]]) -> List[Dict]:
        """Create list of grouped candidates to batch.

        :param candidates: list of lists of candidates to score
            for each sentence
        :return: grouped candidates info
        """
        tokenized_candidates_input_ids = []
        for sentence_candidates in candidates:
            tokenized_sentence_candidates = self.tokenizer(
                sentence_candidates,
                add_special_tokens=False,
                padding=False,
                truncation='do_not_truncate',
            )
            tokenized_candidates_input_ids.append(
                tokenized_sentence_candidates['input_ids']
            )

        # make candidates with moved [MASK] token
        candidates_info = []
        for i, tokenized_sentence_candidates in enumerate(
                tokenized_candidates_input_ids
        ):
            cur_list_input_ids = []
            cur_list_indices = []
            cur_list_answers = []
            for j, tokenized_candidate in enumerate(
                    tokenized_sentence_candidates
            ):
                for k in range(len(tokenized_candidate)):
                    # make substitution for [MASK] token in tokenized candidate
                    # for others keep [UNK] token (it has won't have attention)
                    cur_candidate = [self.tokenizer.unk_token_id] * len(
                        tokenized_candidate
                    )
                    cur_candidate[k] = self.tokenizer.mask_token_id
                    cur_list_input_ids.append(cur_candidate)
                    cur_list_indices.append((i, j))
                    cur_list_answers.append(tokenized_candidate[k])
            candidates_info.append({
                # input ids of tokenized candidate
                'input_ids': cur_list_input_ids,
                # indices of sentence and candidate in input lists
                'indices': cur_list_indices,
                # token ids of answers on MASK
                'answers': cur_list_answers
            })

        # group similar candidates for each sentence
        grouped_candidates_info = []
        for sentence_info in candidates_info:
            input_ids_with_sorting_indices = sorted(
                enumerate(sentence_info['input_ids']), key=lambda x: x[1]
            )
            sort_indices = [x[0] for x in input_ids_with_sorting_indices]

            sentence_grouped_input_ids = []
            sentence_grouped_indices = []
            sentence_grouped_answers = []

            cur_list_indices = []
            cur_list_answers = []
            # not to treat first element
            prev_element = sentence_info['input_ids'][sort_indices[0]]
            for idx in sort_indices:
                cur_element = sentence_info['input_ids'][idx]
                if cur_element != prev_element:
                    sentence_grouped_input_ids.append(prev_element)
                    sentence_grouped_indices.append(cur_list_indices)
                    sentence_grouped_answers.append(cur_list_answers)
                    prev_element = cur_element
                    cur_list_indices = []
                    cur_list_answers = []
                cur_list_indices.append(sentence_info['indices'][idx])
                cur_list_answers.append(sentence_info['answers'][idx])

            # process remain lists
            sentence_grouped_input_ids.append(prev_element)
            sentence_grouped_indices.append(cur_list_indices)
            sentence_grouped_answers.append(cur_list_answers)

            grouped_candidates_info.append({
                'input_ids': sentence_grouped_input_ids,
                'indices': sentence_grouped_indices,
                'answers': sentence_grouped_answers
            })

        return grouped_candidates_info

    def _score_batch(self, batch: Dict[str, List]) -> List[List[float]]:
        """Scoring a batch of candidates.

        :param batch: dict with input_ids, attentions_masks, answers

        :returns: list of results
        """
        # find mask indexes
        mask_indexes = [
            torch.nonzero(x == self.tokenizer.mask_token_id).item()
            for x in batch['input_ids']
        ]

        # create a valid BatchEncoding object to run model
        max_len = max([len(x) for x in batch['input_ids']])

        # pad all input_ids with [PAD] token id to max length
        input_ids_list = [
            F.pad(x, (0, max_len - len(x)), 'constant',
                  self.tokenizer.pad_token_id)
            for x in batch['input_ids']
        ]
        input_ids = torch.stack(input_ids_list, dim=0)

        # pad all attention_mask with 0 to max length
        attention_mask_list = [
            F.pad(x, (0, max_len - len(x)), 'constant', 0)
            for x in batch['attention_mask']
        ]
        attention_mask = torch.stack(attention_mask_list, dim=0)

        # create token_type_ids filled with 0
        token_type_ids = torch.zeros_like(
            input_ids, dtype=torch.long, device=self.device
        )

        model_input = BatchEncoding({
            'input_ids': input_ids,
            'attention_mask': attention_mask,
            'token_type_ids': token_type_ids
        })

        with torch.no_grad():
            # run model
            model_output = self.model(**model_input)[0].cpu().detach()
            log_probs = F.log_softmax(model_output, dim=-1)

            results = []
            for i, sentence_answers in enumerate(batch['answers']):
                results.append(
                    log_probs[i][mask_indexes[i]][sentence_answers].tolist()
                )

        return results

    def _update_results(
            self, score_results: List[List[List[float]]],
            results_update: List[List[float]],
            indices_to_process: List[List[Tuple[int, int]]]
    ) -> List[List[List[float]]]:
        """Update results according to batch results.

        :param score_results: current results of all candidates
            for all sentences
        :param results_update: results from processing the batch
        :param indices_to_process: indices of sentences and candidates
            that was processed in batch

        :returns: updated results
        """
        for i, group_results_update in enumerate(results_update):
            for j, group_member_result_update in enumerate(
                    group_results_update
            ):
                sentence_idx, candidate_idx = indices_to_process[i][j]
                score_results[sentence_idx][candidate_idx].append(
                    group_member_result_update
                )
        return score_results
