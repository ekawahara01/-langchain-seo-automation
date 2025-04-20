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
# すでにある import の下あたりに追加
from fastapi import FastAPI
import os
from datetime import datetime
from notion_client import Client  # 最新のLangChainで利用可能
notion = Client(auth=os.getenv("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"))
# FastAPI インスタンスが未定義なら定義（既にある場合はこの行は不要）
app = FastAPI()

# NotionDB 初期化
notion = NotionDB(notion_api_key=os.getenv("NOTION_TOKEN"))

# NotionのデータベースID（共有されたもの）
DATABASE_ID = "1dbdd486fbf08044a694000cae707fde"

@app.get("/test_notion")
def test_notion():
    new_data = {
        "Name": "LangChain Notion連携テスト",  # タイトル列
        "期限": datetime.now().strftime("%Y-%m-%d"),  # Date型
        "状態": "進行中"  # セレクト型
    }

    try:
        result = notion.create_page(database_id=DATABASE_ID, properties=new_data)
        return {"status": "success", "url": result.get("url")}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
from notion_client import Client
from datetime import datetime

# Notionクライアントを初期化
notion = Client(auth=os.getenv("NOTION_TOKEN"))

# テスト書き込みエンドポイント
@app.get("/test_notion")
def test_notion():
    new_data = {
        "parent": {"database_id": "1dbdd486fbf08044a694000cae707fde"},
        "properties": {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": "LangChain × Notion テスト"
                        }
                    }
                ]
            },
            "期限": {
                "date": {
                    "start": datetime.now().strftime("%Y-%m-%d")
                }
            },
            "状態": {
                "select": {
                    "name": "進行中"
                }
            }
        }
    }

    res = notion.pages.create(**new_data)
    return {"status": "success", "id": res["id"]}


