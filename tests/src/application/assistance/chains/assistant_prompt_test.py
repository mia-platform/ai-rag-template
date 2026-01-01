import pytest

from src.application.assistance.chains.assistant_prompt import (
    DEFAULT_SYSTEM_TEMPLATE,
    DEFAULT_USER_TEMPLATE,
    AssistantPromptBuilder,
    AssistantPromptTemplate,
    RequiredVariableMissingError,
    UserDefinedVariableMissingError,
)


def test_assistant_prompt_builder():
    builder = AssistantPromptBuilder()
    assistant_prompt = builder.add_variable("new_variable").append_to_system_template("\nYou MUST also consider this new variable: {new_variable}.").build()

    assert isinstance(assistant_prompt, AssistantPromptTemplate)
    assert "new_variable" in assistant_prompt.input_variables
    assert "You MUST also consider this new variable: {new_variable}." in assistant_prompt.system_template


def test_assistant_prompt_builder_duplicate_variable():
    builder = AssistantPromptBuilder()

    with pytest.raises(ValueError) as excinfo:
        builder.add_variable("output_text")

    assert str(excinfo.value) == "Variable output_text already exists."


def test_assistant_prompt_builder_unused_variable():
    builder = AssistantPromptBuilder()
    builder.add_variable("unused_variable")

    with pytest.raises(UserDefinedVariableMissingError) as excinfo:
        builder.build()

    assert str(excinfo.value) == "User-defined variable 'unused_variable' is not used in either the system or user template."


def test_missing_required_variable():
    builder = AssistantPromptBuilder(system_template="{chat_history}", user_template="{query}")

    with pytest.raises(RequiredVariableMissingError) as excinfo:
        builder.build()

    assert str(excinfo.value) == "Required variable 'output_text' is not used in either the system or user template."


def test_correct_template():
    system_template = "{output_text} {chat_history} {custom_variable}"
    user_template = "{query}"
    builder = AssistantPromptBuilder(system_template=system_template, user_template=user_template)
    builder.add_variable("custom_variable")

    prompt = builder.build()

    assert prompt.system_template == system_template
    assert prompt.user_template == user_template


def test_load_system_template_from_file(tmp_path):
    builder = AssistantPromptBuilder()
    filepath = tmp_path / "test_file.txt"
    with open(filepath, "w", encoding="utf-8") as file:
        file.write("Test system template")
    builder.load_system_template_from_file(filepath)
    assert builder.system_template == "Test system template"


def test_load_user_template_from_file(tmp_path):
    builder = AssistantPromptBuilder()
    filepath = tmp_path / "test_file.txt"
    with open(filepath, "w", encoding="utf-8") as file:
        file.write("Test user template")
    builder.load_user_template_from_file(filepath)
    assert builder.user_template == "Test user template"


def test_load_system_template_from_file_not_exists(tmp_path):
    builder = AssistantPromptBuilder()
    filepath = tmp_path / "test_file.txt"
    with pytest.raises(FileNotFoundError):
        builder.load_system_template_from_file(filepath)


def test_load_user_template_from_file_not_exists(tmp_path):
    builder = AssistantPromptBuilder()
    filepath = tmp_path / "test_file.txt"
    with pytest.raises(FileNotFoundError):
        builder.load_user_template_from_file(filepath)


def test_build_user_template_from_file(tmp_path):
    prompt_content = "{query} {chat_history} {output_text} {custom_variable}"
    builder = AssistantPromptBuilder()
    filepath = tmp_path / "test_file.txt"
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(prompt_content)

    builder.load_user_template_from_file(filepath)

    builder.build()

    assert builder.user_template == prompt_content
    assert builder.system_template == DEFAULT_SYSTEM_TEMPLATE


def test_build_system_template_from_file(tmp_path):
    prompt_content = "{query} {chat_history} {output_text} {custom_variable}"
    builder = AssistantPromptBuilder()
    filepath = tmp_path / "test_file.txt"
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(prompt_content)

    builder.load_system_template_from_file(filepath)

    builder.build()

    assert builder.system_template == prompt_content
    assert builder.user_template == DEFAULT_USER_TEMPLATE
