import json
import unittest

import grc2prompt


class Grc2PromptTests(unittest.TestCase):
    def test_extract_json_from_markdown_fence(self):
        parsed = grc2prompt.extract_json('```json\n{"rules":[]}\n```')
        self.assertEqual(parsed, {"rules": []})

    def test_extract_json_from_noisy_response(self):
        parsed = grc2prompt.extract_json('Here is the result:\n{"company":"Acme","rules":[]}\nDone.')
        self.assertEqual(parsed["company"], "Acme")

    def test_validate_passport_defaults_and_rule_normalization(self):
        passport = grc2prompt.validate_passport(
            {
                "rules": [
                    {
                        "severity": "INVALID",
                        "rule": "Do not paste secrets into public AI tools.",
                        "action": "NOPE",
                    }
                ]
            }
        )
        self.assertEqual(passport["passport_version"], "1.0")
        self.assertEqual(passport["company"], "Unnamed Organization")
        self.assertEqual(passport["rules"][0]["id"], "R001")
        self.assertEqual(passport["rules"][0]["severity"], "MEDIUM")
        self.assertEqual(passport["rules"][0]["action"], "WARN")

    def test_render_passport_text_contains_rule(self):
        passport = grc2prompt.validate_passport(
            {
                "company": "Acme",
                "policy_name": "AI Usage",
                "effective_scope": "Employees",
                "rules": [
                    {
                        "id": "R007",
                        "severity": "HIGH",
                        "rule": "Review AI output before customer use.",
                        "action": "WARN",
                    }
                ],
            }
        )
        text = grc2prompt.render_passport_text(passport)
        self.assertIn("Company: Acme", text)
        self.assertIn("R007 [HIGH] Review AI output before customer use.", text)
        self.assertIn("-> On violation: WARN", text)

    def test_validate_command_prints_json(self):
        raw = json.dumps({"company": "Acme", "rules": []})
        parsed = grc2prompt.validate_passport(grc2prompt.extract_json(raw))
        self.assertEqual(parsed["company"], "Acme")


if __name__ == "__main__":
    unittest.main()
