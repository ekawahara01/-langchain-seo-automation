from fastapi import FastAPI
from pydantic import BaseModel
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from github import Github
import os

app = FastAPI()

class PromptRequest(BaseModel):
    prompt: str

@app.post("/run")
def run_chain(request: PromptRequest):
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    response = llm([HumanMessage(content=request.prompt)])
    return {"response": response.content}

class RepoRequest(BaseModel):
    repo_name: str
    description: str = "Langchain SEO Auto Repo"
    private: bool = True

@app.post("/create_repo")
def create_repo(data: RepoRequest):
    print("🔧 [LOG] GitHub API呼び出し前")

    github_token = os.getenv("GITHUB_TOKEN")
    g = Github(github_token)
    user = g.get_user()

    print("📦 [LOG] GitHubユーザー取得済み")

    repo = user.create_repo(
        name=data.repo_name,
        description=data.description,
        private=data.private,
        auto_init=True
    )

    print(f"✅ [LOG] リポジトリ作成完了: {repo.clone_url}")
    return {"url": repo.clone_url, "status": "created"}


