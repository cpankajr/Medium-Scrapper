# -*- coding: utf-8 -*-

from django.test import TestCase

from MediumScrapperApp.utils import remove_html_from_string, get_tag_suggestion

import logging
logger = logging.getLogger(__name__)

"""
Tests for utils.py
"""


class UtilsFunctions(TestCase):

    def setUp(self):
        logger.info(
            "Setting up the test environment for utils.py...")

    """
        function tested: remove_html_from_string
        input:
            raw_str: raw stringwith html
        expected :
            string after removing html tags
    """

    def test_remove_html_from_string(self):
        logger.info("Testing remove_html_from_string...")
        input_strings = ["<html>htmlcontent</html>",
                         """<div class="stylish" style="display: none;">htmlindiv</div>""", ""]
        expected_strings = ["htmlcontent", "htmlindiv", ""]
        output_strings = []
        for test_string in input_strings:
            output = remove_html_from_string(test_string)
            output_strings.append(output)

        self.assertEqual(output_strings, expected_strings)

    """
        function tested: get_tag_suggestion
        input:
            query: user query (tag)
        expected output:
            list of suggested tags based on query
    """

    def test_get_tag_suggestion(self):
        logger.info("Testing get_tag_suggestion...")
        input_queries = ["ram", "python", "python2345"]
        expected_tags = [['Ramadan', 'Ramblings', 'Ramen', 'Rams', 'Rambo Last Blood'], [
            'Python', 'Python3', 'Python Programming', 'Python Web Developer', 'Python Flask'], []]
        output_tags = []
        for test_query in input_queries:
            output = get_tag_suggestion(test_query)
            output_tags.append(output)
        self.assertEqual(output_tags, expected_tags)