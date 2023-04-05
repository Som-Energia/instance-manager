import asyncio

import paramiko
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from gestor.manager import manager
from gestor.models.instance import InstanceModel
from gestor.schemas.instance import Instance
from gestor.utils.database import Base, SessionLocal, engine

Base.metadata.create_all(bind=engine)

router = APIRouter()

key = paramiko.RSAKey.from_private_key_file("gestor-key")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
async def root():
    return {"message": "Hello API!"}


@router.post("/instances/deploy/pr")
async def instance_from_pull_request(
    repository: str, pull_request: int
) -> dict[str, str]:
    """Deploys a new instance from a pull request"""
    try:
        await manager.start_instance_from_pull_request(repository, pull_request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "Added new instance from pull request task"}


@router.delete("/instances/{instance_name}")
async def undeploy_instance(instance_name: str, db: Session = Depends(get_db)) -> None:
    instance = InstanceModel.get_instance(db=db, instance_name=instance_name)
    if instance is None:
        raise HTTPException(status_code=404, detail="Instance not found")
    else:
        await Instance.from_orm(instance).undeploy()


@router.get("/instances/", response_model=list[Instance])
def read_instances(db: Session = Depends(get_db)):
    instances = InstanceModel.get_instances(db=db)
    return instances


@router.get("/instances/{instance_name}", response_model=Instance)
def read_instance(instance_name: str, db: Session = Depends(get_db)):
    instance = InstanceModel.get_instance(db=db, instance_name=instance_name)
    if instance is None:
        raise HTTPException(status_code=404, detail="Instance not found")
    return instance


@router.get("/instances/{instance_name}/logs", response_model=str)
async def read_instance_logs(instance_name: str, db: Session = Depends(get_db)) -> str:
    instance = InstanceModel.get_instance(db=db, instance_name=instance_name)
    if instance is None:
        raise HTTPException(status_code=404, detail="Instance not found")
    return await Instance.from_orm(instance).logs()


@router.websocket("/ssh")
async def ssh(websocket: WebSocket):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname="192.168.49.2", username="root", pkey=key, port=32152)
    chan = ssh.invoke_shell(term="vt100", width=200, height=50)
    await websocket.accept()

    async def read_chan():
        while not chan.exit_status_ready():
            if chan.recv_ready():
                data = chan.recv(1024).decode("utf-8")
                await websocket.send_text(data)
            await asyncio.sleep(0.05)

    read_task = asyncio.create_task(read_chan())

    try:
        while True:
            try:
                message = await asyncio.wait_for(websocket.receive_text(), timeout=0.05)
                chan.send(message.encode("utf-8"))
            except asyncio.TimeoutError:
                pass

    except WebSocketDisconnect:
        ssh.close()
        read_task.cancel()
