import logging
import unittest

from src.logging_config import configure_logging, get_logger


class TestLoggingConfig(unittest.TestCase):

    def test_get_logger_returns_named_logger(self):
        logger = get_logger("llmops.test")

        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "llmops.test")

    def test_configure_logging_runs(self):
        configure_logging()

        logger = get_logger("llmops.test")
        self.assertTrue(logger.isEnabledFor(logging.INFO))

    
    def test_logger_emits_info_message(self):
        logger = get_logger("llmops.test")

        with self.assertLogs("llmops.test", level="INFO") as captured:
            logger.info("Validation started")

        self.assertIn("Validation started", captured.output[0])


if __name__ == "__main__":
    unittest.main()