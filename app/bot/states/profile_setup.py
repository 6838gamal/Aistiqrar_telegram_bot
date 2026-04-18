from aiogram.fsm.state import State, StatesGroup


class ProfileSetup(StatesGroup):
    specialization = State()   # الخطوة 1: التخصص
    skills         = State()   # الخطوة 2: المهارات
    experience     = State()   # الخطوة 3: سنوات الخبرة
    portfolio      = State()   # الخطوة 4: رابط المحفظة (اختياري)
    rate           = State()   # الخطوة 5: السعر (اختياري)
