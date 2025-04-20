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
from pydantic import BaseModel
from github import Github
import os

class RepoRequest(BaseModel):
    repo_name: str
    description: str = "LangChain SEO Auto Repo"
    private: bool = True

@app.post("/create_repo")
@app.post("/create_repo")
def create_repo(data: RepoRequest):
    print("=== GitHub API 呼び出し前 ===")

    github_token = os.getenv("GITHUB_TOKEN")
    g = Github(github_token)

    try:
        user = g.get_user()
        print("=== ユーザー情報取得成功 ===")
        
        repo = user.create_repo(
            name=data.repo_name,
            description=data.description,
            private=data.private,
            auto_init=True
        )
        print(f"=== リポジトリ作成成功: {repo.clone_url} ===")

        return {"url": repo.clone_url, "status": "created"}

    except Exception as e:
        print(f"=== エラー発生 ===\n{str(e)}")
        return {"error": str(e), "status": "failed"}

