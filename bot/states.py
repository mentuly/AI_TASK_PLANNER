from aiogram.fsm.state import State, StatesGroup

class PlanState(StatesGroup):
    waiting_for_task = State()