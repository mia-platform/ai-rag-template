import os
from langchain_core.prompts import ChatPromptTemplate

DEFAULT_SYSTEM_TEMPLATE = \
"""
You are an AI assistant.

---
{output_text} {chat_history}
You MUST reply to Human question using the same language of the question.
""" 

DEFAULT_USER_TEMPLATE = "{query}"

class AssistantPromptTemplate(ChatPromptTemplate):
    @property
    def system_template(self):
        if self.messages[0].prompt.template is None:
            raise ValueError("System template is not defined.")
        return self.messages[0].prompt.template
    
    @property
    def user_template(self):
        if self.messages[1].prompt.template is None:
            raise ValueError("User template is not defined.")
        return self.messages[1].prompt.template

class RequiredVariableMissingError(Exception):
    def __init__(self, variable):
        super().__init__(f"Required variable '{variable}' is not used in either the system or user template.")

class UserDefinedVariableMissingError(Exception):
    def __init__(self, variable):
        super().__init__(f"User-defined variable '{variable}' is not used in either the system or user template.")

class AssistantPromptBuilder:
    def __init__(
        self,
        system_template: str = None,
        user_template: str = None):
        self.required_variables = [
            "output_text",  # this is the output of the document aggregation chain
            "chat_history",  # this is the chat history, coming from the user,
            "query",  # this is the query from the user
        ]
        self.user_added_variables = []
        self.__system_template = system_template if system_template is not None else DEFAULT_SYSTEM_TEMPLATE
        self.__user_template = user_template if user_template is not None else DEFAULT_USER_TEMPLATE
        
    @property
    def system_template(self):
        return self.__system_template

    @property
    def user_template(self):
        return self.__user_template

    def add_variable(self, variable):
        if variable in self.required_variables or variable in self.user_added_variables:
            raise ValueError(f"Variable {variable} already exists.")
        self.user_added_variables.append(variable)
        return self

    def _validate(self):
        for variable in self.required_variables:
            wrapped_variable = "{" + variable + "}"
            if wrapped_variable not in self.__system_template and wrapped_variable not in self.__user_template:
                raise RequiredVariableMissingError(variable)
        for variable in self.user_added_variables:
            wrapped_variable = "{" + variable + "}"
            if wrapped_variable not in self.__system_template and wrapped_variable not in self.__user_template:
                raise UserDefinedVariableMissingError(variable)

    def append_to_system_template(self, string):
        self.__system_template += string
        return self
    
    def append_to_user_template(self, string):
        self.__user_template += string
        return self

    def build(self):
        self._validate()
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.__system_template),
            ("user", self.__user_template),
        ])
        return AssistantPromptTemplate(
            messages=prompt.messages
        )

    def _retrieve_prompt_from_file(self, filepath):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"The file '{filepath}' does not exist.")
        try:
            with open(filepath, 'r', encoding="utf-8") as file:
                data = file.read()
            return data
        except IOError as e:
            raise IOError(f"An error occurred while reading the file '{filepath}': {str(e)}")
    
    
    def load_system_template_from_file(self, filepath):
        """
        Load the system template from a file. This operation will override the current system template.
        """
        self.__system_template = self._retrieve_prompt_from_file(filepath)

    def load_user_template_from_file(self, filepath):
        """
        Load the user template from a file. This operation will override the current user template.
        """
        self.__user_template = self._retrieve_prompt_from_file(filepath)
