# main.py (整理対応版 - Notion構成分類・アーカイブ対応)

from fastapi import FastAPI, Request from pydantic import BaseModel from langchain.chat_models import ChatOpenAI from langchain.schema import HumanMessage from github import Github from notion_client import Client from datetime import datetime import os from dotenv import load_dotenv

.env読み込み

load_dotenv()

FastAPI 初期化

app = FastAPI()

トークン確認ログ

print("GITHUB_TOKEN:", os.getenv("GITHUB_TOKEN")) print("NOTION_TOKEN:", os.getenv("NOTION_TOKEN"))

--- LangChain 実行用プロンプト受取 ---

class PromptRequest(BaseModel): prompt: str

@app.post("/run") def run_chain(request: PromptRequest): llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0) response = llm([HumanMessage(content=request.prompt)]) return {"response": response.content}

--- GitHubリポジトリ作成API ---

class RepoRequest(BaseModel): repo_name: str description: str = "Langchain SEO Auto Repo" private: bool = True

@app.post("/create_repo") def create_repo(data: RepoRequest): print("🔧 [LOG] GitHub API呼び出し前")

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

--- Notion 整理対応API ---

notion = Client(auth=os.getenv("NOTION_TOKEN"))

@app.post("/update_notion_status") def update_notion_status(request: Request): data = await request.json() parent_url = data.get("parent_page_url") parent_id = parent_url.split("-")[-1]

print("[START] 整理開始対象:", parent_id)

try:
    pages = notion.search(filter={"property": "object", "value": "page"})
    count_total = 0
    count_untitled = 0
    count_archived = 0
    duplicates = {}
    seen_titles = set()

    for page in pages["results"]:
        parent = page.get("parent", {})
        if parent.get("type") != "page_id" or parent.get("page_id") != parent_id:
            continue

        props = page.get("properties", {})
        title_data = props.get("title", {}).get("title", [])
        title = title_data[0]["plain_text"] if title_data else ""
        count_total += 1

        if not title:
            count_untitled += 1
            notion.pages.update(
                page_id=page["id"],
                properties={"Tags": {"multi_select": [{"name": "未分類"}]}}
            )
            print("[分類] タイトルなし → 未分類タグ追加:", page["id"])
        elif title in seen_titles:
            duplicates[title] = duplicates.get(title, 1) + 1
            print("[重複] 統合候補:", title)
        else:
            seen_titles.add(title)

        if not props:
            count_archived += 1
            notion.pages.update(page_id=page["id"], archived=True)
            print("[アーカイブ] 空ページ:", page["id"])

    print(f"[完了] 対象: {count_total}件 / 未分類: {count_untitled} / アーカイブ: {count_archived}")
    return {
        "status": "completed",
        "classified": count_untitled,
        "archived": count_archived,
        "duplicates": duplicates
    }

except Exception as e:
    print("[ERROR]", str(e))
    return {"status": "error", "message": str(e)}


