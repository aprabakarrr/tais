from rasa_core.evaluate import _generate_trackers, collect_story_predictions

from rasa_core import utils
from rasa_core.utils import AvailableEndpoints
from rasa_core.run import load_agent
from rasa_core.interpreter import NaturalLanguageInterpreter
import re
import os
from os import listdir
from os.path import isfile, join

from prompt_toolkit.styles import Style
import argparse


PASSED_COLOR = utils.bcolors.OKGREEN
FAILED_COLOR = utils.bcolors.FAIL
CORE_DIR = 'models/dialogue'
NLU_DIR = 'models/nlu/current'


parser = argparse.ArgumentParser()

parser.add_argument(
    '--stories', '-s', type=str, default='',
    help='Stories directory (default: tais)'
)
parser.add_argument(
    '--e2e', '--end-to-end', action='store_true',
    help='Use end-to-end evaluation (default: False)'
)

args = parser.parse_args()


def process_failed_stories(failed_story):
    print('\n')
    for line in failed_story.splitlines():
        if re.search('<!--.*-->', line):
            error_prediction = re.search('<!--(.*)-->', line).group(1).split(':')
            print("Deuuuuu\n\n")
            print(error_prediction)
            print("Deuuuuu\n\n")
            utils.print_color(line, FAILED_COLOR)
        else:
            print(line)
    print('\n')

def run_evaluation(stories_to_evaluate,
              fail_on_prediction_errors=False,
              max_stories=None,
              use_e2e=False):

    _endpoints = AvailableEndpoints.read_endpoints(None)
    _interpreter = NaturalLanguageInterpreter.create(NLU_DIR)

    _agent = load_agent(CORE_DIR,
                        interpreter=_interpreter,
                        endpoints=_endpoints)

    completed_trackers = _generate_trackers(stories_to_evaluate, _agent,
                                        max_stories, use_e2e)               
                                                                            
    story_evaluation, _ = collect_story_predictions(completed_trackers, _agent,
                                                fail_on_prediction_errors,
                                                use_e2e)
    
    _failed_stories = story_evaluation.failed_stories

    if len(_failed_stories) == 0:
        success_message = 'All the stories have passed for {}!!'.format(stories_to_evaluate)
        utils.print_color('\n' + '=' * len(success_message), PASSED_COLOR)
        utils.print_color(success_message, PASSED_COLOR)
        utils.print_color('=' * len(success_message) + '\n', PASSED_COLOR)
    else:
        for failed_story in _failed_stories:
            process_failed_stories(failed_story.export_stories())

if __name__ == '__main__':
    stories_path = parser.parse_args().stories
    use_e2e = parser.parse_args().e2e

    stories_to_evaluate = []

    if os.path.isdir(stories_path):
        if not stories_path.endswith('/'):
            stories_path += '/'

        stories_files = [f for f in listdir(stories_path) if
                         isfile(join(stories_path, f))]

        for file in stories_files:
            run_evaluation(stories_path + file, False, None, use_e2e)
    else:
        run_evaluation(stories_path, False, None, use_e2e)
