from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .apps import ChooseWordConfig


class BertValidationTests(APITestCase):
    """Test case to test validation of input for BERT algorithm."""
    url = reverse('choose_word_bert')
    tokenizer = ChooseWordConfig.bert_tokenizer

    def test_ok(self):
        """Test good case."""
        data = {
            'text_parts': ['London is the', 'Great Britain.'],
            'candidates': [['capital', 'city']]
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_400_wrong_lengths(self):
        """Test error with lengths."""
        data = {
            'text_parts': ['London is the', 'Great Britain.', ''],
            'candidates': [['capital', 'city']]
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('non_field_errors' in response.data)
        self.assertTrue(
            'Wrong lengths' in response.data['non_field_errors'][0]
        )

    def test_400_unk(self):
        """Test error with [UNK] token."""
        data = {
            'text_parts': [f'London is the {self.tokenizer.unk_token}',
                           'Great Britain.'],
            'candidates': [['capital', 'city']]
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('text_parts' in response.data)
        self.assertTrue(
            self.tokenizer.unk_token in response.data['text_parts'][0][0]
        )

    def test_400_mask(self):
        """Test error with [MASK] token."""
        data = {
            'text_parts': [f'London is the {self.tokenizer.mask_token}',
                           'Great Britain.'],
            'candidates': [['capital', 'city']]
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('text_parts' in response.data)
        self.assertTrue(
            self.tokenizer.mask_token in response.data['text_parts'][0][0]
        )

    def test_400_not_enough_candidates(self):
        """Test error with not enough candidates."""
        data = {
            'text_parts': ['London is the', 'Great Britain.'],
            'candidates': [['capital']]
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('candidates' in response.data)
        self.assertTrue(
            'at least 2' in response.data['candidates'][0][0]
        )

    def test_400_duplicate_candidates(self):
        """Test error with duplicate candidates."""
        data = {
            'text_parts': ['London is the', 'Great Britain.'],
            'candidates': [['capital', 'city', 'capital']]
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('candidates' in response.data)
        self.assertTrue(
            'duplicate candidates' in response.data['candidates'][0][0]
        )

    def test_400_empty_candidates(self):
        """Test error with empty candidates."""
        data = {
            'text_parts': ['London is the', 'Great Britain.'],
            'candidates': [['capital', 'city', '']]
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('candidates' in response.data)
        self.assertTrue(
            'empty candidates' in response.data['candidates'][0][0]
        )

    def test_400_big_candidates(self):
        """Test error with empty candidates."""
        data = {
            'text_parts': ['London is the', 'Great Britain.'],
            'candidates': [['capital '*200, 'city']]
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('candidates' in response.data)
        self.assertTrue(
            'Too big candidate' in response.data['candidates'][0][0]
        )

    def test_400_unk_candidates(self):
        """Test error with [UNK] token in candidates."""
        data = {
            'text_parts': ['London is the', 'Great Britain.'],
            'candidates': [[f'{self.tokenizer.unk_token}', 'city']]
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('candidates' in response.data)
        self.assertTrue(
            self.tokenizer.unk_token in response.data['candidates'][0][0][0]
        )

    def test_400_mask_candidates(self):
        """Test error with [MASK] token in candidates."""
        data = {
            'text_parts': ['London is the', 'Great Britain.'],
            'candidates': [[f'{self.tokenizer.mask_token}', 'city']]
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('candidates' in response.data)
        self.assertTrue(
            self.tokenizer.mask_token in response.data['candidates'][0][0][0]
        )

    def test_very_long_sentence(self):
        """Test working with very long sentences."""
        data = {
            'text_parts': ['London is the '*1000, ' Great Britain.'*1000],
            'candidates': [['capital', 'city']]
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GPTValidationTests(APITestCase):
    """Test case to test validation of input for GPT algorithm."""
    url = reverse('choose_word_gpt')
    tokenizer = ChooseWordConfig.gpt_tokenizer

    def test_ok(self):
        """Test good case."""
        data = {
            'text_parts': ['London is the', 'Great Britain.'],
            'candidates': [['capital', 'city']]
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_400_wrong_lengths(self):
        """Test error with lengths."""
        url = reverse('choose_word_gpt')
        data = {
            'text_parts': ['London is the', 'Great Britain.', ''],
            'candidates': [['capital', 'city']]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('non_field_errors' in response.data)
        self.assertTrue(
            'Wrong lengths' in response.data['non_field_errors'][0]
        )

    def test_400_unk(self):
        """Test error with [UNK] token."""
        url = reverse('choose_word_gpt')
        data = {
            'text_parts': [f'London is the {self.tokenizer.unk_token}',
                           'Great Britain.'],
            'candidates': [['capital', 'city']]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('text_parts' in response.data)
        self.assertTrue(
            self.tokenizer.unk_token in response.data['text_parts'][0][0]
        )

    def test_400_not_enough_candidates(self):
        """Test error with not enough candidates."""
        url = reverse('choose_word_gpt')
        data = {
            'text_parts': ['London is the', 'Great Britain.'],
            'candidates': [['capital']]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('candidates' in response.data)
        self.assertTrue(
            'at least 2' in response.data['candidates'][0][0]
        )

    def test_400_duplicate_candidates(self):
        """Test error with duplicate candidates."""
        url = reverse('choose_word_gpt')
        data = {
            'text_parts': ['London is the', 'Great Britain.'],
            'candidates': [['capital', 'city', 'capital']]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('candidates' in response.data)
        self.assertTrue(
            'duplicate candidates' in response.data['candidates'][0][0]
        )

    def test_400_empty_candidates(self):
        """Test error with empty candidates."""
        url = reverse('choose_word_gpt')
        data = {
            'text_parts': ['London is the', 'Great Britain.'],
            'candidates': [['capital', 'city', '']]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('candidates' in response.data)
        self.assertTrue(
            'empty candidates' in response.data['candidates'][0][0]
        )

    def test_400_unk_candidates(self):
        """Test error with [UNK] token in candidates."""
        url = reverse('choose_word_gpt')
        data = {
            'text_parts': ['London is the', 'Great Britain.'],
            'candidates': [[f'{self.tokenizer.unk_token}', 'city']]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('candidates' in response.data)
        self.assertTrue(
            self.tokenizer.unk_token in response.data['candidates'][0][0][0]
        )

    def test_very_long_sentence(self):
        """Test working with very long sentences."""
        url = reverse('choose_word_gpt')
        data = {
            'text_parts': ['London is the '*1000, ' Great Britain.'*1000],
            'candidates': [['capital', 'city']]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

