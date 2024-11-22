from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from src.adapters.inbound.api import MarathonController
from src.application.services import MarathonService
from src.infrastructure.uow import SqlAlchemyUnitOfWork

def create_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
    )

    # 의존성 주입
    marathon_service = MarathonService(uow=SqlAlchemyUnitOfWork())
    marathon_controller = MarathonController(marathon_service)
    
    # 라우터 등록
    app.include_router(marathon_controller.router)
    
    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)