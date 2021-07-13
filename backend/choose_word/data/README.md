# SdamGia Choose Word Dataset

Dataset is crawled from https://ege.sdamgia.ru/ and consists of questions 32-38 for English exam. You can use this dataset to measure the quality of the model.

## Description

Dataset is consists of 63 texts with 7 tasks per text, that gives 441 questions. Each text has 7 gaps represented by `_____` sequence. The goal is to select one word from list of four words for each gap.

Fields meaning:
* `title` - title of the text;
* `text` - text with gaps;
* `gaps` - tasks for gaps:
    * `task_num` - number of task in exam: 32-38;
    * `choices` - choices for answer;
    * `answer` - number of true answer (starts from 1).
