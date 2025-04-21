
    print("🔧 [LOG] GitHub API呼び出し前")

    github_token = os.getenv("GITHUB_TOKEN")
    g = Github(github_token)
    user = g.get_user()# main.py（Notion + GitHub リポジトリ作成 + LangChain 簡易テスト対応）
from fastapi import FastAPI
from pydantic import BaseModel
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from github import Github
from notion_client import Client
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()
app = FastAPI()
print("GITHUB_TOKEN:", os.getenv("GITHUB_TOKEN"))
print("NOTION_TOKEN:", os.getenv("NOTION_TOKEN"))
# --- LangChain 実行用プロンプト受取 ---
class PromptRequest(BaseModel):
    prompt: str

@app.post("/run")
def run_chain(request: PromptRequest):
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    response = llm([HumanMessage(content=request.prompt)])
    return {"response": response.content}

# --- GitHubリポジトリ作成API ---
class RepoRequest(BaseModel):
    repo_name: str
    description: str = "Langchain SEO Auto Repo"
    private: bool = True

@app.post("/create_repo")
def create_repo(data: RepoRequest):

    print("📦 [LOG] GitHubユーザー取得済み")

    repo = user.create_repo(
        name=data.repo_name,
        description=data.description,
        private=data.private,
        auto_init=True
    )

    print(f"✅ [LOG] リポジトリ作成完了: {repo.clone_url}")
    return {"url": repo.clone_url, "status": "created"}

# --- Notion ステータス更新API ---
notion = Client(auth=os.getenv("NOTION_TOKEN"))
DATABASE_ID = "1dcdd486fbf0802682c6dd20aa73c2ff"

@app.post("/update_notion_status")
def update_notion_status(data: dict):
    """
    data = {
        "page_id": "対象ページのID",
        "status": "完了" or "未完"
    }
    """
    try:
        notion.pages.update(
            page_id=data["page_id"],
            properties={
                "LangChain実行状況": {
                    "select": {"name": data["status"]}
                }
            }
        )
        return {"status": "success", "updated": data["status"]}
    except Exception as e:
        return {"status": "error", "message": str(e)}




