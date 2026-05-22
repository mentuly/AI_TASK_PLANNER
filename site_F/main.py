from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from core.repository import delete_task, get_tasks_with_steps, mark_done, get_task_owner
from core.auth import get_user_by_token

app = FastAPI()

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

    task_list = await get_tasks_with_steps(int(user_id))

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
    
    # один запит
    result = await get_tasks_with_steps(int(user_id))
    
    return result


@app.post("/done/{task_id}")
async def done(task_id: int, request: Request):
    user_id = request.cookies.get("user_id")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authorized")
    
    # перевірка чи таск належить юзеру
    task_owner = await get_task_owner(int(task_id))
    
    if task_owner != int(user_id):
        raise HTTPException(status_code=403, detail="Forbidden: Task does not belong to this user")
    
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

@app.delete("/delete/{task_id}")
async def delete_task_endpoint(task_id: int, request: Request):
    user_id = request.cookies.get("user_id")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authorized")
    
    # перевіряємо чи таск належить юзеру
    task_owner = await get_task_owner(task_id)
    
    if task_owner != int(user_id):
        raise HTTPException(status_code=403, detail="Forbidden: Task does not belong to this user")
    
    await delete_task(task_id)
    return {"status": "ok"}