import unittest
from libs.aws.awscommands import AWSCommands


class DummyLogger:
    def __init__(self):
        self.records = []
    def log(self, text):
        self.records.append(text)


class AWSCommandsTests(unittest.TestCase):
    def test_process_url_logs_s3_links(self):
        logger = DummyLogger()
        commands = AWSCommands(None, logger)
        commands.process_url('http://bucket.amazonaws.com/path')
        self.assertEqual(logger.records, ['http://bucket.amazonaws.com/path'])

    def test_process_url_ignores_other_links(self):
        logger = DummyLogger()
        commands = AWSCommands(None, logger)
        commands.process_url('http://example.com/')
        self.assertEqual(logger.records, [])


if __name__ == '__main__':
    unittest.main()
