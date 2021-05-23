from typing import List

import torch
from transformers.tokenization_utils import PreTrainedTokenizer
from transformers import GPT2LMHeadModel


class GPTScorerSentence:
    """Class for scoring all candidates for correction by GPT2 model."""

    def __init__(
            self,
            model: GPT2LMHeadModel,
            tokenizer: PreTrainedTokenizer,
            max_length: int = 1024,
            device: int = -1
    ):
        """Init object.

        :param model: Bert model for MLM from transformers library
        :param tokenizer: tokenizer for Bert model
        :param max_length: maximum number of tokens to process
        :param device: id of device
        """
        self.device = torch.device('cpu' if device < 0 else f'cuda:{device}')
        self.model = model.to(device=self.device)
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __call__(
            self, sentences: List[str]
    ) -> List[float]:
        """Make scoring for all hypotheses.

        :param sentences: list of sentences

        :returns: scores for each sentence
        """
        results = []
        for sentence in sentences:
            results.append(self._score_sentence(sentence))

        return results

    def _score_sentence(self, sentence: str, stride=512) -> float:
        """Calculate perplexity for each sentence.

        :param sentence: sentence to check

        :returns: perplexity of the sentence
        """
        model_input = self.tokenizer(
            sentence,
            add_special_tokens=True,
            truncation='do_not_truncate',
            return_tensors='pt'
        )

        lls = []
        for i in range(0, model_input['input_ids'].size(1), stride):
            begin_loc = max(i + stride - self.max_length, 0)
            end_loc = min(i + stride, model_input['input_ids'].size(1))
            trg_len = end_loc - i  # may be different from stride on last loop
            input_ids = model_input['input_ids'][:, begin_loc:end_loc].to(
                self.device
            )
            target_ids = input_ids.clone()
            target_ids[:, :-trg_len] = -100

            with torch.no_grad():
                outputs = self.model(input_ids, labels=target_ids)
                log_likelihood = outputs[0] * trg_len

            lls.append(log_likelihood)

        ppl = torch.exp(torch.stack(lls).sum() / end_loc).item()
        return ppl
