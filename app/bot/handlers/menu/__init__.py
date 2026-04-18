from .home import router as home_router
from .job import router as job_router
from .profile import router as profile_router
from .categories import router as categories_router
from .suggest import router as suggest_router
from .invite import router as invite_router
from .help import router as help_router
from .lang import router as lang_router
from .favorites import router as favorites_router
from .about import router as about_router
from .contact import router as contact_router
from .subscribe import router as subscribe_router


def setup_menu_routers(dp):
    dp.include_router(lang_router)
    dp.include_router(home_router)
    dp.include_router(job_router)
    dp.include_router(profile_router)
    dp.include_router(categories_router)
    dp.include_router(suggest_router)
    dp.include_router(invite_router)
    dp.include_router(help_router)
    dp.include_router(favorites_router)
    dp.include_router(about_router)
    dp.include_router(contact_router)
    dp.include_router(subscribe_router)
