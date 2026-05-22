from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

from data_storage import append_to_csv
from kpi_calculator import build_conclusion, calculate_kpis
from llm_client import (
    ask_llm_json,
    get_config_status,
    get_runtime_mode,
    test_openai_connection,
)
from prompts import (
    ARTIFACT_GENERATION_SCHEMA,
    ARTIFACT_GENERATION_SYSTEM_PROMPT,
    FEEDBACK_ANALYSIS_SCHEMA,
    FEEDBACK_ANALYSIS_SYSTEM_PROMPT,
    TASK_ANALYSIS_SCHEMA,
    TASK_ANALYSIS_SYSTEM_PROMPT,
    build_artifact_generation_prompt,
    build_feedback_analysis_prompt,
    build_task_analysis_prompt,
)


BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
KPI_RESULTS_PATH = DATA_DIR / "kpi_results.csv"
SAMPLE_FEEDBACK_PATH = DATA_DIR / "sample_feedback.csv"


st.set_page_config(
    page_title="AI Process Efficiency Assistant",
    page_icon="AI",
    layout="wide",
)


def show_runtime_mode() -> None:
    mode = get_runtime_mode()
    config_status = get_config_status()

    if mode == "real":
        st.success("Real OpenAI API mode is active.")
    elif mode == "mock":
        st.warning(
            "Mock mode is active. Add valid OPENAI_API_KEY to .env for real AI responses."
        )
    elif mode == "missing_key":
        st.warning(
            "Mock mode is active. Add valid OPENAI_API_KEY to .env for real AI responses."
        )
    elif mode == "real_missing_key":
        st.error("OpenAI API error: API key is missing. APP_MODE=real requires OPENAI_API_KEY.")
    else:
        st.warning(
            "Mock mode is active. Add valid OPENAI_API_KEY to .env for real AI responses."
        )

    with st.expander("OpenAI configuration check", expanded=False):
        st.write(f"`.env` path: `{config_status['env_path']}`")
        st.write(f"`.env` file found: `{config_status['env_exists']}`")
        st.write(f"`APP_MODE`: `{config_status['app_mode']}`")
        st.write(f"`OPENAI_MODEL`: `{config_status['model']}`")
        st.write(f"`OPENAI_API_KEY` detected: `{config_status['key_detected']}`")
        st.write(
            f"`OPENAI_API_KEY` placeholder value: `{config_status['key_is_placeholder']}`"
        )
        st.write(f"`safe key preview`: `{config_status['key_preview']}`")
        st.write(f"`runtime mode`: `{config_status['runtime_mode']}`")


def render_connection_test() -> None:
    if st.button("Test OpenAI connection"):
        with st.spinner("Testing OpenAI connection..."):
            result = test_openai_connection()

        if result.get("ok"):
            st.success("OpenAI connection works.")
        else:
            st.error(result.get("error", "Unknown OpenAI connection error."))
            st.caption(f"LLM response source: {result.get('source', 'error')}")
            st.caption(f"Used runtime mode: {result.get('runtime_mode', get_runtime_mode())}")


def show_list(title: str, items: list[str]) -> None:
    st.subheader(title)
    if items:
        for item in items:
            st.markdown(f"- {item}")
    else:
        st.caption("No items returned.")


def get_llm_data_or_stop(
    result: dict[str, Any],
    input_text: str | None = None,
) -> dict[str, Any] | None:
    if result.get("ok"):
        data = result.get("data")
        return data if isinstance(data, dict) else {}

    message = result.get("error", "OpenAI request failed.")
    if result.get("source") == "mock":
        st.warning(
            "Mock mode is active. This module will not generate AI analysis until a valid OpenAI API key and billing are configured."
        )
    else:
        st.error(message)
    if input_text is not None:
        st.caption(f"Analyzed input length: {len(input_text)} characters")
    st.caption(f"Used runtime mode: {result.get('runtime_mode', get_runtime_mode())}")
    st.caption(f"LLM response source: {result.get('source', 'error')}")
    return None


def show_llm_debug(input_text: str, result: dict[str, Any]) -> None:
    st.caption(f"Analyzed input length: {len(input_text)} characters")
    st.caption(f"Used runtime mode: {result.get('runtime_mode', get_runtime_mode())}")
    st.caption(f"LLM response source: {result.get('source', 'unknown')}")


def show_input_summary(title: str, text: str, limit: int | None = None) -> None:
    st.subheader(title)
    preview = text if limit is None else text[:limit]
    st.info(preview)


def render_improved_task_description(improved: dict[str, Any]) -> None:
    st.subheader("Improved task description")
    st.markdown(f"**Context:** {improved.get('context', '')}")
    st.markdown(f"**Goal:** {improved.get('goal', '')}")
    st.markdown(f"**User story:** {improved.get('user_story', '')}")

    sections = [
        ("Functional requirements", "functional_requirements"),
        ("Acceptance criteria", "acceptance_criteria"),
        ("Edge cases", "edge_cases"),
        ("Error states", "error_states"),
        ("Analytics requirements", "analytics_requirements"),
        ("QA notes", "qa_notes"),
        ("Risks", "risks"),
        ("Dependencies", "dependencies"),
    ]
    for title, key in sections:
        show_list(title, improved.get(key, []))


def render_task_quality_tab() -> None:
    st.header("Task Quality Analyzer")
    st.write(
        "This module evaluates whether a product/project task is ready for refinement, development, and QA."
    )

    default_task = (
        "Потрібно додати новий екран верифікації користувача, де буде "
        "показано статус документів і пояснення, що потрібно зробити далі."
    )
    task_description = st.text_area(
        "Product/project task description",
        value=default_task,
        height=180,
    )
    st.caption("This action sends one request to OpenAI API.")

    if st.button("Analyze task quality", type="primary"):
        if not task_description.strip():
            st.warning("Please enter a task description first.")
            return

        with st.spinner("Analyzing task quality..."):
            llm_result = ask_llm_json(
                TASK_ANALYSIS_SYSTEM_PROMPT,
                build_task_analysis_prompt(task_description),
                TASK_ANALYSIS_SCHEMA,
                max_output_tokens=2200,
            )

        result = get_llm_data_or_stop(llm_result, task_description)
        if result is None:
            return

        show_input_summary("Analyzed task", task_description)

        score = int(result.get("task_quality_score", 0))
        st.metric("Task quality score", f"{score}/100")
        st.progress(max(0, min(score, 100)) / 100)

        col1, col2 = st.columns(2)
        with col1:
            show_list("Detected elements", result.get("detected_elements", []))
        with col2:
            show_list(
                "Missing or weak elements",
                result.get("missing_or_weak_elements", []),
            )

        show_list("Recommendations", result.get("recommendations", []))
        render_improved_task_description(
            result.get("improved_task_description", {})
        )
        show_llm_debug(task_description, llm_result)


def render_dict_section(value: dict[str, Any]) -> None:
    for key, item in value.items():
        label = key.replace("_", " ").title()
        if isinstance(item, list):
            show_list(label, [str(list_item) for list_item in item])
        else:
            st.markdown(f"**{label}:** {item}")


def render_artifact_section(title: str, value: Any) -> None:
    st.subheader(title)

    if isinstance(value, dict):
        render_dict_section(value)
    elif isinstance(value, list):
        if value and all(isinstance(item, dict) for item in value):
            st.dataframe(pd.DataFrame(value), width="stretch")
        else:
            for item in value:
                st.markdown(f"- {item}")
    else:
        st.write(value)


def render_artifact_generator_tab() -> None:
    st.header("Artifact Generator")
    st.write(
        "This module generates product and project artifacts based on the user's idea: PRD, user stories, acceptance criteria, QA checklist, and risk register."
    )

    idea = st.text_area(
        "Short product/project idea",
        value=(
            "Створити AI-модуль для аналізу користувацького фідбеку "
            "та формування продуктових гіпотез."
        ),
        height=160,
    )

    artifact_options = [
        "Product Brief / PRD",
        "User stories",
        "Acceptance criteria",
        "QA checklist",
        "Risk register",
    ]
    selected_artifacts = st.multiselect(
        "Artifacts to generate",
        artifact_options,
        default=artifact_options,
    )
    st.caption("This action sends one request to OpenAI API.")

    artifact_key_map = {
        "Product Brief / PRD": "product_brief",
        "User stories": "user_stories",
        "Acceptance criteria": "acceptance_criteria",
        "QA checklist": "qa_checklist",
        "Risk register": "risk_register",
    }

    if st.button("Generate artifacts", type="primary"):
        if not idea.strip():
            st.warning("Please enter an idea first.")
            return
        if not selected_artifacts:
            st.warning("Please select at least one artifact.")
            return

        with st.spinner("Generating artifacts..."):
            llm_result = ask_llm_json(
                ARTIFACT_GENERATION_SYSTEM_PROMPT,
                build_artifact_generation_prompt(idea, selected_artifacts),
                ARTIFACT_GENERATION_SCHEMA,
                max_output_tokens=2600,
            )

        result = get_llm_data_or_stop(llm_result, idea)
        if result is None:
            return

        show_input_summary("Generated artifacts for", idea)

        for artifact_name in selected_artifacts:
            key = artifact_key_map[artifact_name]
            render_artifact_section(artifact_name, result.get(key, []))
        show_llm_debug(idea, llm_result)


def load_sample_feedback_text() -> str:
    if not SAMPLE_FEEDBACK_PATH.exists():
        return ""
    sample_df = pd.read_csv(SAMPLE_FEEDBACK_PATH)
    if "feedback" not in sample_df.columns:
        return ""
    return "\n".join(sample_df["feedback"].dropna().astype(str).tolist())


def render_feedback_analyzer_tab() -> None:
    st.header("Feedback Analyzer")
    st.write(
        "This module analyzes user feedback and converts unstructured comments into themes, problems, hypotheses, and recommended metrics."
    )

    feedback_items = st.text_area(
        "User feedback items, one per line",
        value=(
            "1. Не розумію, чому мої документи відхилили.\n"
            "2. Дуже довго проходить перевірка.\n"
            "3. Хотілося б бачити статус кожного документа.\n"
            "4. Незрозуміло, які саме фото треба завантажити.\n"
            "5. Після відхилення не пояснюється причина."
        )
        or load_sample_feedback_text(),
        height=240,
    )
    st.caption("This action sends one request to OpenAI API.")

    if st.button("Analyze feedback", type="primary"):
        if not feedback_items.strip():
            st.warning("Please enter at least one feedback item.")
            return

        with st.spinner("Analyzing feedback..."):
            llm_result = ask_llm_json(
                FEEDBACK_ANALYSIS_SYSTEM_PROMPT,
                build_feedback_analysis_prompt(feedback_items),
                FEEDBACK_ANALYSIS_SCHEMA,
                max_output_tokens=1800,
            )

        result = get_llm_data_or_stop(llm_result, feedback_items)
        if result is None:
            return

        show_input_summary("Analyzed feedback sample", feedback_items, limit=500)

        col1, col2 = st.columns(2)
        with col1:
            show_list(
                "Main feedback themes",
                result.get("main_feedback_themes", []),
            )
            show_list(
                "Repeated user problems",
                result.get("repeated_user_problems", []),
            )
        with col2:
            st.subheader("Sentiment summary")
            sentiment = result.get("sentiment_summary", {})
            st.metric("Positive", sentiment.get("positive", 0))
            st.metric("Neutral", sentiment.get("neutral", 0))
            st.metric("Negative", sentiment.get("negative", 0))
            st.markdown(f"**Overall:** {sentiment.get('overall', 'Unknown')}")

        show_list("Product hypotheses", result.get("product_hypotheses", []))
        show_list("Recommended metrics", result.get("recommended_metrics", []))

        priority_table = result.get("priority_table", [])
        st.subheader("Priority table")
        if priority_table:
            st.dataframe(pd.DataFrame(priority_table), width="stretch")
        else:
            st.caption("No priority table returned.")
        show_llm_debug(feedback_items, llm_result)


def render_kpi_chart(
    time_before: float,
    time_after: float,
    quality_before: float,
    quality_after: float,
) -> None:
    chart_df = pd.DataFrame(
        {
            "Metric": ["Time, minutes", "Time, minutes", "Quality", "Quality"],
            "Stage": ["Before AI", "After AI", "Before AI", "After AI"],
            "Value": [time_before, time_after, quality_before, quality_after],
        }
    )
    fig = px.bar(
        chart_df,
        x="Metric",
        y="Value",
        color="Stage",
        barmode="group",
        text_auto=True,
        title="Before and After AI Comparison",
    )
    fig.update_layout(legend_title_text="", yaxis_title="Value")
    st.plotly_chart(fig, width="stretch")


def render_saved_kpi_results() -> None:
    st.subheader("Saved KPI results")
    if not KPI_RESULTS_PATH.exists() or KPI_RESULTS_PATH.stat().st_size == 0:
        st.caption("No saved KPI results yet.")
        return

    results_df = pd.read_csv(KPI_RESULTS_PATH)
    if results_df.empty:
        st.caption("No saved KPI results yet.")
        return

    st.dataframe(results_df.tail(10), width="stretch")


def render_kpi_calculator_tab() -> None:
    st.header("KPI Impact Calculator")
    st.write(
        "This module evaluates the impact of AI on process efficiency using before/after KPI values."
    )

    with st.form("kpi_form"):
        task_name = st.text_input("Task name", value="Prepare sprint task description")

        col1, col2 = st.columns(2)
        with col1:
            time_before = st.number_input(
                "Time before AI, minutes",
                min_value=0.0,
                value=90.0,
                step=5.0,
            )
            quality_before = st.slider(
                "Quality before AI, 1-10",
                min_value=1,
                max_value=10,
                value=6,
            )
            clarifications_before = st.number_input(
                "Clarifications before AI",
                min_value=0.0,
                value=5.0,
                step=1.0,
            )
            defects_before = st.number_input(
                "Defects/risks before AI",
                min_value=0.0,
                value=4.0,
                step=1.0,
            )

        with col2:
            time_after = st.number_input(
                "Time after AI, minutes",
                min_value=0.0,
                value=55.0,
                step=5.0,
            )
            quality_after = st.slider(
                "Quality after AI, 1-10",
                min_value=1,
                max_value=10,
                value=8,
            )
            clarifications_after = st.number_input(
                "Clarifications after AI",
                min_value=0.0,
                value=2.0,
                step=1.0,
            )
            defects_after = st.number_input(
                "Defects/risks after AI",
                min_value=0.0,
                value=2.0,
                step=1.0,
            )

        cost_per_hour = st.number_input(
            "Cost per hour, optional",
            min_value=0.0,
            value=40.0,
            step=5.0,
        )

        submitted = st.form_submit_button("Calculate and save KPI impact")

    if submitted:
        if not task_name.strip():
            st.warning("Please enter a task name.")
            return

        if time_before == 0 or clarifications_before == 0 or defects_before == 0:
            st.warning(
                "Some baseline values are 0, so the related percentage reductions will be calculated as 0%."
            )

        metrics = calculate_kpis(
            time_before,
            time_after,
            quality_before,
            quality_after,
            clarifications_before,
            clarifications_after,
            defects_before,
            defects_after,
            cost_per_hour,
        )
        conclusion = build_conclusion(metrics)

        st.subheader("Calculated metrics")
        metric_cols = st.columns(3)
        metric_cols[0].metric(
            "Time Saving %",
            f"{metrics['time_saving_percent']:.2f}%",
        )
        metric_cols[1].metric(
            "Quality Change",
            f"{metrics['quality_change']:.2f}",
        )
        metric_cols[2].metric(
            "Efficiency Index",
            f"{metrics['efficiency_index']:.4f}",
        )

        metric_cols = st.columns(3)
        metric_cols[0].metric(
            "Clarification Reduction %",
            f"{metrics['clarification_reduction_percent']:.2f}%",
        )
        metric_cols[1].metric(
            "Defect/Risk Change %",
            f"{metrics['defect_risk_change_percent']:.2f}%",
        )
        metric_cols[2].metric(
            "Cost Saving",
            f"{metrics['cost_saving']:.2f}",
        )

        st.info(conclusion)
        render_kpi_chart(time_before, time_after, quality_before, quality_after)

        row = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "task_name": task_name,
            "time_before_minutes": time_before,
            "time_after_minutes": time_after,
            "quality_before": quality_before,
            "quality_after": quality_after,
            "clarifications_before": clarifications_before,
            "clarifications_after": clarifications_after,
            "defects_before": defects_before,
            "defects_after": defects_after,
            "cost_per_hour": cost_per_hour,
            **metrics,
            "conclusion": conclusion,
        }
        append_to_csv(KPI_RESULTS_PATH, row)
        st.success(f"Saved KPI result to {KPI_RESULTS_PATH}")

    render_saved_kpi_results()


def main() -> None:
    st.title("AI Process Efficiency Assistant")
    st.caption(
        "MVP platform for supporting product and project team workflows with AI and evaluating the impact of AI on process efficiency."
    )
    st.write(
        "This platform was developed as an experimental MVP for a bachelor thesis on the impact of artificial intelligence technologies on the efficiency of product and project management processes in IT companies."
    )
    show_runtime_mode()
    render_connection_test()

    tabs = st.tabs(
        [
            "Task Quality Analyzer",
            "Artifact Generator",
            "Feedback Analyzer",
            "KPI Impact Calculator",
        ]
    )

    with tabs[0]:
        render_task_quality_tab()
    with tabs[1]:
        render_artifact_generator_tab()
    with tabs[2]:
        render_feedback_analyzer_tab()
    with tabs[3]:
        render_kpi_calculator_tab()


if __name__ == "__main__":
    main()
