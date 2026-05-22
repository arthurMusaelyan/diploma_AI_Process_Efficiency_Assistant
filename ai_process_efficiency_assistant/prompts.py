"""Prompts and JSON schemas for AI-assisted product/project workflows."""

from __future__ import annotations


TASK_ANALYSIS_SYSTEM_PROMPT = """
You are an expert Product Manager, Project Manager, Business Analyst, and QA Lead.
Analyze only the task description provided by the user.
Do not invent unrelated features.
Do not give generic output.
Every detected element, missing element, recommendation, and improved task description must be directly connected to the user's input.
If the user writes about verification, analyze verification.
If the user writes about PDF export, analyze PDF export.
If the user writes about advertising, analyze advertising.
If the input is vague or not an IT product/project task, still analyze it as a task and explain what is missing to make it usable for a product/project team.
"""


TASK_ANALYSIS_SCHEMA = {
    "name": "task_quality_analysis",
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "task_quality_score",
            "detected_elements",
            "missing_or_weak_elements",
            "recommendations",
            "improved_task_description",
        ],
        "properties": {
            "task_quality_score": {
                "type": "integer",
                "minimum": 0,
                "maximum": 100,
            },
            "detected_elements": {
                "type": "array",
                "items": {"type": "string"},
            },
            "missing_or_weak_elements": {
                "type": "array",
                "items": {"type": "string"},
            },
            "recommendations": {
                "type": "array",
                "items": {"type": "string"},
            },
            "improved_task_description": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "context",
                    "goal",
                    "user_story",
                    "functional_requirements",
                    "acceptance_criteria",
                    "edge_cases",
                    "error_states",
                    "analytics_requirements",
                    "qa_notes",
                    "risks",
                    "dependencies",
                ],
                "properties": {
                    "context": {"type": "string"},
                    "goal": {"type": "string"},
                    "user_story": {"type": "string"},
                    "functional_requirements": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "acceptance_criteria": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "edge_cases": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "error_states": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "analytics_requirements": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "qa_notes": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "risks": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "dependencies": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
            },
        },
    },
}


ARTIFACT_GENERATION_SYSTEM_PROMPT = """
You are an expert Product Manager, Business Analyst, Project Manager, and QA Lead.
Generate selected product/project artifacts based only on the user input.
Do not create unrelated examples.
Use practical IT product team language.
Acceptance criteria must be testable.
QA checklist must include happy path, edge cases, error states, and regression risks.
Risk register must include relevant product, technical, process, data/security risks where applicable.
"""


ARTIFACT_GENERATION_SCHEMA = {
    "name": "artifact_generation",
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "product_brief",
            "user_stories",
            "acceptance_criteria",
            "qa_checklist",
            "risk_register",
        ],
        "properties": {
            "product_brief": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "context",
                    "problem",
                    "goal",
                    "target_users",
                    "main_scenario",
                    "functional_requirements",
                    "non_functional_requirements",
                    "success_metrics",
                ],
                "properties": {
                    "context": {"type": "string"},
                    "problem": {"type": "string"},
                    "goal": {"type": "string"},
                    "target_users": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "main_scenario": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "functional_requirements": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "non_functional_requirements": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "success_metrics": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
            },
            "user_stories": {
                "type": "array",
                "items": {"type": "string"},
            },
            "acceptance_criteria": {
                "type": "array",
                "items": {"type": "string"},
            },
            "qa_checklist": {
                "type": "array",
                "items": {"type": "string"},
            },
            "risk_register": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["risk", "probability", "impact", "mitigation"],
                    "properties": {
                        "risk": {"type": "string"},
                        "probability": {"type": "string"},
                        "impact": {"type": "string"},
                        "mitigation": {"type": "string"},
                    },
                },
            },
        },
    },
}


FEEDBACK_ANALYSIS_SYSTEM_PROMPT = """
You are an expert Product Manager and Product Analyst.
Analyze only the feedback provided by the user.
Do not invent feedback that is not present.
Identify themes, repeated problems, sentiment, product hypotheses, recommended metrics, and priorities.
If feedback is about verification, focus on verification.
If feedback is about payment, focus on payment.
If feedback is about PDF export, focus on PDF export.
If feedback is about advertising, focus on advertising.
"""


FEEDBACK_ANALYSIS_SCHEMA = {
    "name": "feedback_analysis",
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "main_feedback_themes",
            "repeated_user_problems",
            "sentiment_summary",
            "product_hypotheses",
            "recommended_metrics",
            "priority_table",
        ],
        "properties": {
            "main_feedback_themes": {
                "type": "array",
                "items": {"type": "string"},
            },
            "repeated_user_problems": {
                "type": "array",
                "items": {"type": "string"},
            },
            "sentiment_summary": {
                "type": "object",
                "additionalProperties": False,
                "required": ["positive", "neutral", "negative", "overall"],
                "properties": {
                    "positive": {"type": "integer"},
                    "neutral": {"type": "integer"},
                    "negative": {"type": "integer"},
                    "overall": {"type": "string"},
                },
            },
            "product_hypotheses": {
                "type": "array",
                "items": {"type": "string"},
            },
            "recommended_metrics": {
                "type": "array",
                "items": {"type": "string"},
            },
            "priority_table": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["problem", "frequency", "impact", "priority"],
                    "properties": {
                        "problem": {"type": "string"},
                        "frequency": {"type": "integer"},
                        "impact": {"type": "string"},
                        "priority": {"type": "string"},
                    },
                },
            },
        },
    },
}


def build_task_analysis_prompt(task_description: str) -> str:
    return f"""
Analyze the following product/project task description.

User task description:
\"\"\"
{task_description}
\"\"\"

Important:
- Base your analysis only on this task.
- Do not use generic examples.
- If the task is about verification, analyze verification.
- If the task is about export to PDF, analyze export to PDF.
- If the task is about advertising, analyze advertising.
- If the task is about feedback analysis, analyze feedback analysis.
- Improved task description must be a better version of the same task, not a different task.
"""


def build_artifact_generation_prompt(idea: str, selected_artifacts: list[str]) -> str:
    return f"""
Generate the selected product/project artifacts for the following idea.

User idea:
\"\"\"
{idea}
\"\"\"

Selected artifacts:
{", ".join(selected_artifacts)}

Important:
- Generate only content relevant to the user idea.
- Do not invent a different product.
- Use practical IT product team language.
- Acceptance criteria should be testable.
- QA checklist should include happy path, edge cases, error states, and regression risks.
- Risk register should include product, technical, process, and data/security risks if relevant.
"""


def build_feedback_analysis_prompt(feedback_text: str) -> str:
    return f"""
Analyze the following user feedback.

Feedback:
\"\"\"
{feedback_text}
\"\"\"

Important:
- Count repeated issues based only on the feedback.
- If feedback is mostly about verification, focus on verification.
- If feedback is about payment, focus on payment.
- If feedback is about export to PDF, focus on export to PDF.
- If feedback is about advertising, focus on advertising.
- Do not use unrelated examples.
- Product hypotheses should directly address the problems found in the feedback.
"""
