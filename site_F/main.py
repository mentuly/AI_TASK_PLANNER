from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from core.repository import get_tasks, get_steps, mark_done
from core.auth import get_user_by_token

app = FastAPI()

# 🔥 підключаємо templates


templates = Jinja2Templates(directory="site_F/templates")
app.mount("/static", StaticFiles(directory="site_F/static"), name="static")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request,
        "home.html",
        {"request": request, "user_id": request.cookies.get("user_id"), "page": "home"}
    )

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(
        request,
        "login.html",
        {"request": request, "user_id": request.cookies.get("user_id"), "page": "login"}
    )

@app.get("/dashboard")
async def dashboard(request: Request):
    user_id = request.cookies.get("user_id")

    if not user_id:
        return RedirectResponse("/login")

    tasks = await get_tasks(int(user_id))
    task_list = []
    for task_id, title, is_done in tasks:
        steps = await get_steps(task_id)
        total_minutes = 0
        steps_data = []
        for step_title, step_description, step_minutes in steps:
            total_minutes += step_minutes
            steps_data.append({
                "title": step_title,
                "description": step_description,
                "minutes": step_minutes,
                "is_done": False
            })

        task_list.append({
            "id": task_id,
            "title": title,
            "is_done": is_done,
            "total_minutes": total_minutes,
            "steps": steps_data
        })

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "request": request,
            "page": "dashboard",
            "user_id": user_id,
            "tasks": task_list,
            "summaryTotal": len(task_list),
            "summaryDone": sum(1 for task in task_list if task["is_done"]),
            "summaryPending": sum(1 for task in task_list if not task["is_done"])
        }
    )

@app.get("/settings")
async def settings(request: Request):
    user_id = request.cookies.get("user_id")

    if not user_id:
        return RedirectResponse("/login")

    return templates.TemplateResponse(
        request,
        "settings.html",
        {"request": request, "page": "settings"}
    )


@app.get("/tasks")
async def api_tasks(request: Request):
    user_id = request.cookies.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Not authorized")

    tasks = await get_tasks(int(user_id))

    result = []

    for task_id, title, is_done in tasks:
        steps = await get_steps(task_id)

        total_minutes = 0

        steps_data = []
        for s in steps:
            step_title, step_description, step_minutes = s

            total_minutes += step_minutes

            steps_data.append({
                "title": step_title,
                "description": step_description,
                "minutes": step_minutes,
                "is_done": False  # поки що
            })

        result.append({
            "id": task_id,
            "title": title,
            "is_done": is_done,
            "total_minutes": total_minutes,
            "steps": steps_data
        })

    return result


@app.post("/done/{task_id}")
async def done(task_id: int):
    await mark_done(task_id)
    return {"status": "ok"}


@app.get("/auth/{token}")
async def auth(token: str):
    user_id = await get_user_by_token(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    response = RedirectResponse(url="/dashboard")

    response.set_cookie(
        key="user_id",
        value=str(user_id),
        httponly=True,
        samesite="lax"
    )

    return response