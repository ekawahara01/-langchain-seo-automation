from fastapi import FastAPI
from pydantic import BaseModel
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

app = FastAPI()

class PromptRequest(BaseModel):
    prompt: str

@app.post("/run")
def run_chain(request: PromptRequest):
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    response = llm([HumanMessage(content=request.prompt)])
    return {"response": response.content}
