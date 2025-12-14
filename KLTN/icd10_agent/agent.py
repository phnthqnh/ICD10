from google.adk.agents import Agent
from .systerm_prompt import ROOT_PROMPTS
from .tools import predict_icd10, get_info_icd10, search_icd10

root_agent = Agent(
    model='gemini-2.5-flash',
    name='ICD10_Agent',
    description='Agent ICD10 hỗ trợ người dùng tra cứu bệnh qua triệu chứng hoặc hình ảnh',
    instruction=ROOT_PROMPTS,
    tools=[predict_icd10, get_info_icd10, search_icd10]
)
