import json
import time

import numpy as np
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import BertTestItemSerializer, GPTTestItemSerializer
from .utils import process_text_bert, process_text_gpt
from .apps import ChooseWordConfig


class ChooseWordBertView(APIView):
    """Controller for running BERT algorithm."""

    parser_classes = [JSONParser]

    def post(self, request):
        serializer = BertTestItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        text_parts = data['text_parts']
        candidates = data['candidates']
        results = process_text_bert(text_parts, candidates)
        return Response(data=results)


class ChooseWordGPTView(APIView):
    """Controller for running GPT algorithm."""

    parser_classes = [JSONParser]

    def post(self, request):
        serializer = GPTTestItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        text_parts = data['text_parts']
        candidates = data['candidates']
        results = process_text_gpt(text_parts, candidates)
        return Response(data=results)


class BenchmarkView(APIView):
    """Controller for running benchmark for algorithms."""

    def get(self, request):
        # load data
        with open(ChooseWordConfig.benchmark_data_path, 'r') as inf:
            data = json.load(inf)

        # get results
        results = {}
        processors = {
            'bert': process_text_bert,
            # 'gpt': process_text_gpt
        }
        for processor_name in processors:
            results_processor = {}
            num_tasks = 0
            wall_time = 0
            confidences = []
            is_correct = []
            for task_block in data:
                num_tasks += len(task_block['gaps'])
                # prepare data for running algorithms
                text_parts = task_block['text'].split('_____')
                candidates = [gap['choices'] for gap in task_block['gaps']]
                correct_answers = [gap['answer'] for gap in task_block['gaps']]

                # validate model
                start_time = time.time()
                results_task = processors[processor_name](
                    text_parts, candidates
                )
                end_time = time.time()
                wall_time += end_time - start_time
                confidences += [
                    max(gap_answers) for gap_answers in results_task
                ]
                is_correct += [
                    np.argmax(gap_answers) + 1 == correct_answers[i]
                    for i, gap_answers in enumerate(results_task)
                ]

            # make a grid with confidences
            confidences = np.array(confidences)
            is_correct = np.array(is_correct)
            grid_start = int(np.floor(np.min(confidences*100)/5)*5)

            grid_results = []
            for confidence_percent in range(grid_start, 100, 5):
                confidence = confidence_percent / 100
                indicator = (confidences >= confidence)
                fraction = np.mean(indicator)
                if fraction == 0:
                    accuracy = grid_results[-1]['accuracy']
                else:
                    accuracy = np.mean(is_correct[indicator])
                grid_results.append({
                    'confidence': confidence,
                    'fraction': fraction,
                    'accuracy': accuracy
                })

            # save results
            results_processor['grid_results'] = grid_results
            results_processor['time'] = wall_time
            results_processor['rps'] = num_tasks/wall_time
            results[processor_name] = results_processor

        return Response(data=results)
